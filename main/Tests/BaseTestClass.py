import logging
import os
import pprint
import traceback
import unittest

from CommonCode.TestExecute import Constants as Const
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.TestContext import Test_Context
from CommonCode.TestHelpers import StringMethods
from CommonCode.WebDriver.WebDriverChromeWrapper import WebDriverChromeWrapper
from CommonCode.WebDriver.WebDriverRemoteWrapper import WebDriverRemoteWrapper
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

from TestPages.DashboardPage import DashboardPage
from TestPages.LoginPage import LoginPageForm


class BaseTestClass(unittest.TestCase):
    driver = None
    run_ui_tests = True

    @classmethod
    def setUpClass(cls):
        cls.longMessage = True

        if cls.run_ui_tests:
            cls.driver = cls.setup_web_driver()
            if 'version' in cls.driver.capabilities:
                PrintMessage(f"Browser version: {cls.driver.capabilities['version']}")
            elif 'browserVersion' in cls.driver.capabilities:
                PrintMessage(f"Browser version: {cls.driver.capabilities['browserVersion']}")

            cls.log_in()

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.quit()

    def setUp(self):
        PrintMessage(Const.TEST_HEAD.format(self._testMethodName))

        if self.run_ui_tests:
            self._clear_chrome_browser_database()
            self.dashboard_page = DashboardPage(self.driver)

    def tearDown(self):
        PrintMessage(Const.TEST_TAIL)

    def _clear_chrome_browser_database(self):
        """
        Redux database is used to persist some of the user / web state information between sessions.
        :return:
        """
        self.driver.execute_script("indexedDB.deleteDatabase('Wood Mackenzie beans--Redux Storage');")
        PrintMessage(Const.RELOADING_BROSWER)
        self.driver.refresh()

    def run(self, result=None):
        """
        We need this to take advantage of TestResultEx
        :param result:
        :return:
        """
        # noinspection PyTypeChecker
        super(BaseTestClass, self).run(TestResultEx(result))

    @classmethod
    def log_in(cls):
        login_page = LoginPageForm(cls.driver)
        login_page.perform_login(user_name=Test_Context.test_user['SITE_USER'],
                                 password=Test_Context.test_user['SITE_PASSWORD'])

    @staticmethod
    def setup_browserstack_driver():
        browserstack_details = Test_Context.run_config.load('BrowserStackDetails')
        command_executor = browserstack_details["BROWSERSTACK_URL"].format(browserstack_details["USERNAME"],
                                                                           browserstack_details["ACCESS_KEY"])

        return WebDriverRemoteWrapper(
            command_executor=command_executor,
            desired_capabilities=Test_Context.run_config.load('BrowserStackBrowserCapabilities'))

    @staticmethod
    def _enable_downloads_and_set_download_directory(driver):
        """
        This method enables downloads for chrome driver (disabled by default in headless mode) and sets the default
        download directory
        """
        download_path = os.path.join(os.getcwd(), Test_Context.get_required_folder('downloads'))
        driver.command_executor._commands['send_command'] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_path}}
        driver.execute("send_command", params)

    @staticmethod
    def setup_default_driver():
        if Test_Context.run_headless:
            options = webdriver.ChromeOptions()
            # Jenkins requires to run in headless mode as there is no UI available there
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--ignore-gpu-blacklist")
            options.add_argument("--use-gl")
        else:
            options = None

        driver = WebDriverChromeWrapper(executable_path='chromedriver',
                                        options=options,
                                        service_log_path=BaseTestClass._get_selenium_log_file_name())

        BaseTestClass._enable_downloads_and_set_download_directory(driver)
        driver.set_window_size(width=1920, height=1080)

        return driver

    @staticmethod
    def setup_web_driver():
        """
        Method to setup a webdriver.
        Keeping commented out code as it might be useful to setup other browser's than chrome
        :return:
        """
        if Test_Context.browser_stack:
            return BaseTestClass.setup_browserstack_driver()
        else:
            return BaseTestClass.setup_default_driver()

    @staticmethod
    def _get_selenium_log_file_name():
        try:
            logger = logging.getLogger(Test_Context.log_name)
            log_file_name = logger.handlers[0].stream.log_file_handler.name
            selenium_log_file = log_file_name.replace('.log', '_selenium.log')

        except (AttributeError, IndexError, NameError) as e:
            tb = traceback.format_exc()
            PrintMessage('Encountered exception in BaseTestClass {0}, with args {1}'.format(type(e), e.args))
            PrintMessage(str(e))
            PrintMessage("traceback: {0}".format(tb))

            log_folder = Test_Context.get_required_folder('logging')
            selenium_log_file = f"{log_folder}{f'{StringMethods.get_unique_name()}_selenium.log'}"

        PrintMessage(f"Created selenium log file: {selenium_log_file}")
        return selenium_log_file


class TestResultEx(object):
    """
    Note: We cannot override the test result from unnit test as this is created by unittest framework and passed in.
    See BaseTestClass.run method, the result already comes in.
    What we can do is to hijack it and force in some of our behaviour.
    """

    def __init__(self, result):
        self.result = result

    def __getattr__(self, name):
        return object.__getattribute__(self.result, name)

    def _get_browser_log(self, test):
        if not (hasattr(test, 'driver') and test.driver):
            return ''

        pp = pprint.PrettyPrinter(indent=4)
        browser_logs = [pp.pformat(k) for k in test.driver.get_log('browser')]

        return "\n".join(browser_logs)

    def _get_screenshot_name(self, test, failure_type):
        screenshot_name = f"{test._testMethodName}{StringMethods.get_unique_string(failure_type)}.png"
        return os.path.join(Test_Context.get_required_folder('screenshots'), screenshot_name)

    def _save_screenshot(self, test, error_type):
        file_name = self._get_screenshot_name(test, error_type)
        if test.driver:
            try:
                test.driver.save_screenshot(file_name)
            except TimeoutException:
                PrintMessage("SYSTEM: webdriver TIMED-OUT: exception on attempt to save screenshot")
                PrintMessage("SYSTEM: webdriver session_id: {0}".format(test.driver.session_id))
                PrintMessage("SYSTEM: webdriver capabilities: {0}".format(test.driver.capabilities))
            finally:
                PrintMessage("SYSTEM: saving screenshot complete.")

    def _get_test_comment(self, err, test):
        # BeannieAP-7975 disabling browser log dump
        # test_browser_log_comments = self._get_browser_log(test)
        test_browser_log_comments = ''

        test_error_comment = self._exc_info_to_string(err, test)

        return f"{test_error_comment} \n {test_browser_log_comments}"

    def _process_unlucky_result(self, test, err, list_to_update):
        self.result._mirrorOutput = True
        test_comment = self._get_test_comment(err, test)
        list_to_update.append((test, test_comment))

    def addError(self, test, err):
        """
        Called by unittest framework for each errored test.
        :param test:
        :param err:
        :return:
        """
        self._process_unlucky_result(test, err, self.result.errors)
        self._save_screenshot(test, '_error')

    def addFailure(self, test, err):
        """
        Called by unittest framework for each failed test.
        :param test:
        :param err:
        :return:
        """
        self._process_unlucky_result(test, err, self.result.failures)
        self._save_screenshot(test, '_failure')
