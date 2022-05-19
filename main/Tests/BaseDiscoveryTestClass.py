from CommonCode.TestExecute import Constants as Const
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.TestContext import Test_Context

from TestPages.DiscoveryLoginPage import DiscoveryLoginPageForm
from TestPages.DiscoveryPage import DiscoveryPage
from Tests.BaseTestClass import BaseTestClass


class BaseDiscoveryTestClass(BaseTestClass):

    def setUp(self):
        PrintMessage(Const.TEST_HEAD.format(self._testMethodName))

        if self.run_ui_tests:
            self.discovery_page = DiscoveryPage(self.driver)

    @classmethod
    def log_in(cls):
        login_page = DiscoveryLoginPageForm(cls.driver)
        login_page.perform_login(user_name=Test_Context.test_user['SITE_USER'],
                                 password=Test_Context.test_user['SITE_PASSWORD'])
