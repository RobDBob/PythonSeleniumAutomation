import copy
import itertools
import locale
import multiprocessing
import os
import re
import sys
import time
import unittest
from contextlib import contextmanager

from CommonCode.HelperFunctions import try_execute
from CommonCode.JsonReader import JsonReader
from CommonCode.Libs_API import TestRailUploader
from CommonCode.Libs_API.APIClient_TestRail import TestRailAPIClient
from CommonCode.TestExecute import TestFuncs
from CommonCode.TestExecute.Logging import PrintMessage, StreamToLogger
from CommonCode.TestExecute.TestContext import Test_Context
from CommonCode.TestExecute.TestDiscovery import TestDiscoverySingleTestRun
from CommonCode.TestExecute.TestResult import TestResultEx
from CommonCode.TestExecute.VersionChecking import print_used_library_versions
from CommonCode.TestHelpers.StringMethods import get_unique_name
from CommonCode.TestReporting.ReportGenerator import ReportGenerator


@contextmanager
def poolcontext(*args, **kwargs):
    """
    Pool context
    :param args:
    :param kwargs:
    :return:
    """
    # Setting up process count to 5 if browserstack is used
    processes_count = 5 if Test_Context.browser_stack else None

    pool = multiprocessing.Pool(processes=processes_count, *args, **kwargs)
    yield pool
    pool.terminate()


def upload_results(test_results, test_suite, main_test_context):
    if main_test_context.build_number:
        result_uploader = TestRailUploader.TestRailResultUploader(main_test_context, test_suite)
        result_uploader.process_and_upload(test_results)


def execute_single_suite_and_upload_results(test_suite, test_context, test_user):
    """
    Method to execute tests in parallel
    :return:
    """
    # Setting a global variable for the process itself to use in test execution
    Test_Context.update(test_context)
    Test_Context.log_name = get_unique_name()
    Test_Context.test_user = test_user

    streamer = StreamToLogger(Test_Context.log_name,
                              Test_Context.get_required_folder('logging'))
    PrintMessage(f"Starting PROCESS - this bucket test count: {test_suite.countTestCases()}")

    # noinspection PyTypeChecker
    runner = unittest.TextTestRunner(stream=streamer, resultclass=TestResultEx)

    # Python3 removes references to test within the runner.run > suite > _removeTestAtIndex
    # This behaviour could be overridden but we might get into a new sort of troubles that _removeTestAtIndex is
    # trying to resolve, so we'll make a copy of test suite instead.
    test_suite_copy_for_reporting = copy.deepcopy(test_suite)
    test_results = runner.run(test_suite)
    try_execute(upload_results, test_results, test_suite_copy_for_reporting, Test_Context)

    # this will be used to set status code on automation pipeline
    return len(test_results.failures) + len(test_results.errors)


class RunManager(object):
    def __init__(self, run_data=None):
        Test_Context.update(run_data)

        self._create_framework_folders()
        self._set_locale()

        test_rail_info = Test_Context.test_rail_config
        self.test_rail = TestRailAPIClient(
            test_rail_info['URL'],
            test_rail_info['User'],
            test_rail_info['Password'])

        self.streamer = StreamToLogger(Test_Context.log_name,
                                       Test_Context.get_required_folder('logging'))

        print_used_library_versions()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Place to add post class cleaning steps i.e. delete temp folders if we decide to go this path
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        return

    @staticmethod
    def _create_framework_folders():
        """
        Method creates folders required by the framework
        List of folders to create is available via EnvironmentConfig.yaml file
        :return:
        """
        if Test_Context.environment_config is None or 'required_folders' not in Test_Context.environment_config:
            return

        for folder_key in Test_Context.environment_config['required_folders']:
            folder_to_create = Test_Context.environment_config['required_folders'][folder_key]
            os.makedirs(folder_to_create, exist_ok=True)

    @staticmethod
    def _get_execution_users(path_to_users_file):
        """
        Execution user will be passed in to multiprocessor map utility where it'll be used in respective TestContext-es
        :param path_to_users_file:
        :return:
        """
        # User files might not be available on certain frameworks
        if path_to_users_file:
            return itertools.cycle(JsonReader(path_to_users_file).jsonFile)
        else:
            automation_config = Test_Context.run_config.load("TestAutomation")
            execution_user = {"SITE_USER": automation_config["SITE_USER"],
                              "SITE_PASSWORD": automation_config["SITE_PASSWORD"]}
            return itertools.repeat(execution_user)

    @staticmethod
    def _set_locale():
        """
        setting locale to US as its currently set for this market
        this will come handy in when deciding what thousand separator is when processing results from page

        :return:
        """
        safe_copy = os.environ.copy()

        try:
            os.environ['PYTHONIOENCODING'] = 'utf_8'

            if 'linux' in sys.platform:
                try:
                    locale.setlocale(locale.LC_ALL, 'en_US')
                except locale.Error:

                    os.environ['LC_ALL'] = 'C'
                    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

            elif 'darwin' in sys.platform:
                locale.setlocale(locale.LC_ALL, 'EN_US')
            else:
                locale.setlocale(locale.LC_ALL, 'English_United States.1252')
        except Exception as e:
            PrintMessage(str(e))
            os.environ = safe_copy

    def _get_tests_suites_to_execute(self):
        """
        Returns list of test IDs for given case_type
        Tests potentially could be set in an execution order depending on test priority
        :return: test grouped by class (group iterator: key: test iterator)
        """

        def test_id_filter(test_name, test_rail_ids):
            try:
                test_id = int(re.search(r'C(\d+)', test_name).group(1))
            except AttributeError:
                PrintMessage(f"Failed processing test {test_name}, id failed to extract")
                return False

            return test_id in test_rail_ids

        loader = unittest.TestLoader()
        folder_to_search = './Tests/'
        pattern_to_use = 'Tests*.py'
        all_tests = loader.discover(folder_to_search, pattern=pattern_to_use)

        assert loader.errors == [], str(loader.errors)

        PrintMessage(f"Discovered {all_tests.countTestCases()} tests in folder {folder_to_search} "
                     f"with search pattern {pattern_to_use}")

        all_tests = list(TestFuncs.iterate_tests(all_tests))

        test_run = Test_Context.run_config.load('TestRun_Detail')
        tests = self.test_rail.get_list_of_tests_for_run_id(test_run['RUN_ID'])
        test_ids = [k['case_id'] for k in tests]

        PrintMessage(f"Retrieved {len(test_ids)} tests from TestRail at address: {self.test_rail.base_url} "
                     f"from test run {test_run['RUN_ID']}")

        lambda_expression = lambda x: test_id_filter(x._testMethodName, list(test_ids))
        filtered_tests = list(filter(lambda_expression, all_tests))

        PrintMessage(f"Identified {len(filtered_tests)} tests to execute")

        return itertools.groupby(filtered_tests, lambda x: type(x))

    def _send_report(self, report_recipients, time_taken=0.0):
        """

        :param report_recipients:
        :param time_taken:
        :return:
        """
        if report_recipients is None:
            PrintMessage("No report recipient supplied, skipping report email")
            return

        report_generator = ReportGenerator(self.test_rail)
        report_generator.generate_and_send(report_recipients, Test_Context.build_number, time_taken)

    @staticmethod
    def _get_test_suite_local_execution():
        test_disco = TestDiscoverySingleTestRun()

        if len(Test_Context.test_ids) > 0:
            suite = test_disco.get_suite_from_test_ids(Test_Context.test_ids)
        elif Test_Context.test_attribute:
            suite = test_disco.get_suite_with_attribute(Test_Context.test_attribute)
        else:
            suite = test_disco.get_suite_from_test_class(Test_Context.test_class_names)

        return suite

    @staticmethod
    def _set_exit_code(result):
        """
        Exit code set by test execution
        This is used in building process of tested projects (currently in Direct Data jenkins pipeline)
        :param result:
        :return:
        """
        if result:
            end_message = "All selected tests finished with pass status - exit code - 0"
            exit_code = 0
        else:
            end_message = "Some of selected tests finished with fail status - exit code: 1"
            exit_code = 1

        PrintMessage(end_message)
        return exit_code

    def run_bunch(self,
                  custom_pool_context=None,
                  path_to_users_file=None,
                  post_execution_cb=()):
        """

        :param custom_pool_context: Pool context for multiprocessor execution
        :param path_to_users_file: list of users used in parallel testing, each process runs of a different user
        :param post_execution_cb: list of callbacks to be executed post test execution i.e. upload results up to magic_repo
        :return:
        """
        selected_group_tests = self._get_tests_suites_to_execute()

        start_time = time.time()

        list_of_tests = []
        for key, selected_group_tests in selected_group_tests:
            filtered_tests_suite = unittest.TestSuite()
            filtered_tests_suite.addTests(selected_group_tests)
            list_of_tests.append(filtered_tests_suite)

        PrintMessage(f"Identified {len(list_of_tests)} test buckets for execution")

        execution_users = self._get_execution_users(path_to_users_file)

        custom_pool_context = custom_pool_context if custom_pool_context else poolcontext

        with custom_pool_context() as pool:
            result = pool.starmap(execute_single_suite_and_upload_results,
                                  zip(list_of_tests,
                                      itertools.repeat(Test_Context),
                                      execution_users))

        try_execute(self._send_report, Test_Context.report_recipients, time_taken=time.time() - start_time)

        # Used for zipping up test logs and etc
        for callback in post_execution_cb:
            try_execute(callback, Test_Context)

        PrintMessage('<<<<<<<<<<<<<<<< Automated Test run - complete!>>>>>>>>>>>>>>>>')

        return result

    def execute_tests_on_demand(self, post_execution_cb=()):
        """
        Run tests either from test ids or test class names (partial is ok)
        :param post_execution_cb:
        :return:
        """

        automation_config = Test_Context.run_config.load("TestAutomation")
        Test_Context.test_user = {"SITE_USER": automation_config["SITE_USER"],
                                  "SITE_PASSWORD": automation_config["SITE_PASSWORD"]}

        # test_ids, test_class_names, test_attribute, luf,

        # noinspection PyTypeChecker
        runner = unittest.TextTestRunner(stream=self.streamer)

        suite = self._get_test_suite_local_execution()

        while True:
            test_suite_copy = copy.deepcopy(suite)
            run_result = runner.run(test_suite_copy)

            if not (Test_Context.luf and run_result and run_result.wasSuccessful()):
                break

        # Used for zipping up test logs and etc
        for callback in post_execution_cb:
            try_execute(callback, Test_Context)

        # this sets exit code for when automation is executed as a part of pipeline
        # with specified test groups i.e. in direct beans project
        exit(self._set_exit_code(run_result.wasSuccessful()))
