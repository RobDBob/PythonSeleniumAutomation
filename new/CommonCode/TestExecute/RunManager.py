import copy
import itertools
import locale
import multiprocessing
import os
import platform
import sys
import unittest
from contextlib import contextmanager
from pprint import pformat
from CommonCode.API.ADORequests import AccessTokenEnum, ADORequests
from CommonCode.HelperFunctions import tryExecute
from CommonCode.TestExecute import Constants
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.Objects.TestBucket import TestBucket
from CommonCode.TestExecute.Objects.TestsResultsContainer import TestsResultsContainer
from CommonCode.TestExecute.Objects.TestsToRunContainer import TestsToRunContainer
from CommonCode.TestExecute.PyStormTestResult import PyStormTextTestResult
from CommonCode.TestExecute.TestContext import Test_Context, TestContext
from CommonCode.TestExecute.TestResultsADOUploader import TestResultsADOUploader

# pylint: disable=broad-exception-caught
# pylint: disable=invalid-name
# pylint: disable=unnecessary-dunder-call


@contextmanager
def poolcontext(*args, **kwargs):
    """
    Pool context
    :param args:
    :param kwargs:
    :return:
    """
    availableCores = multiprocessing.cpu_count()
    processesCount = int(availableCores / 3)

    PrintMessage(f"Pool Context. Available cores: {availableCores}, processes count: {processesCount}")

    pool = multiprocessing.Pool(processes=processesCount, *args, **kwargs)
    yield pool
    pool.terminate()


def logFailures(testFailures):
    """
    Log test failures to log files
    Log only if any failures are present
    """
    if not testFailures:
        return

    for failure in testFailures:
        startMessage = failure[0]._testMethodName if isinstance(failure[0], unittest.TestCase) else str(failure[0])

        PrintMessage(f"------------ Error log START for: {startMessage}")
        PrintMessage(f"\n{failure[1]}")
        PrintMessage(f"------------ Error log END for: {startMessage}")


def executeSingleSuiteAndUploadResults(testBucket: TestBucket, topLevelTestContext: TestContext):
    """
    Method to execute tests in parallel
    :return:
    """
    # Setting a global variable for the process itself to use in test execution
    Test_Context.update(topLevelTestContext._settings)

    # Python3 unit test runner removes references to test within the runner.run > suite > _removeTestAtIndex
    # This behaviour could be overridden but we might get into a new sort of troubles that _removeTestAtIndex is
    # trying to resolve, so we'll make a copy of test suite instead.
    testSuite = copy.deepcopy(testBucket.unitTestSuite)

    try:
        if testSuite._tests:
            testClassName = testSuite._tests[0].__class__.__name__
            PrintMessage(f"Starting PROCESS - bucket test count: {testSuite.countTestCases()} for {testClassName}")
    except BaseException:
        PrintMessage(f"Starting PROCESS - this bucket test count: {testSuite.countTestCases()}")

    # noinspection PyTypeChecker
    runner = unittest.TextTestRunner(stream=sys.stdout)
    runner.resultclass = PyStormTextTestResult

    try:
        testResults = runner.run(testSuite)
    except UnicodeEncodeError:
        PrintMessage(f">>>>>>>>>>>>> THIS CLASS IS CAUSING ERROR: '{testClassName}'")

    testResultsContainer = TestsResultsContainer(Test_Context, testResults, testBucket)

    if not Test_Context.getSetting(ConfigOptions.DRY_RUN):
        tryExecute(TestResultsADOUploader(Test_Context).uploadResultsToADO, testResultsContainer)

    # remove duplicates in case of same test having failure & error
    tryExecute(logFailures, testResultsContainer.allFailures)

    # return test method names
    return [k[0]._testMethodName for k in testResultsContainer.allFailures if k and "_testMethodName" in k[0].__dir__()]


class RunManager:
    def __init__(self, testContext: TestContext):
        locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')
        self.testContext = testContext
        self.createFrameworkFolders(self.testContext)
        self._printUsedLibraryVersions()
        self._printConfiguration()

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
        self.setRunState(Constants.RUN_STATE_COMPLETED)

    @staticmethod
    def createFrameworkFolders(testContext: TestContext):
        """
        Method creates folders required by the framework
        List of folders to create is available via EnvironmentConfig.yaml file
        :return:
        """
        for _, value in testContext.setupConfig.getSetting(ConfigOptions.REQUIRED_FOLDERS, {}).items():
            os.makedirs(value, exist_ok=True)

    @staticmethod
    def _setExitCode(result):
        """
        Exit code set by test execution
        This is used in building process of tested projects (currently in Direct Data jenkins pipeline)
        :param result:
        :return:
        """
        if result:
            endMessage = "All selected tests finished with PASS status - exit code - 0"
            exitCode = 0
        else:
            endMessage = "Some of selected tests finished with FAIL status - exit code: 1"
            exitCode = 1

        PrintMessage(endMessage)
        return exitCode

    def _executePostTestCallbacks(self, postExecutionCBs):
        # Used for zipping up test logs and etc
        for callback in postExecutionCBs:
            tryExecute(callback, self.testContext)

    def _printMessagePostTest(self, testBuckets, results):
        totalNumberOfTestsExecuted = sum(len(k.unitTestSuiteTests) for k in testBuckets)
        totalNumberOfPassedTests = totalNumberOfTestsExecuted - len(results)
        try:
            passRate = 100 * ((totalNumberOfPassedTests) / totalNumberOfTestsExecuted)
        except BaseException:
            passRate = float(0)

        passRateMessage = f"{totalNumberOfPassedTests}/{totalNumberOfTestsExecuted} ({format(passRate, '.2f')}% pass)"
        runId = self.testContext.getSetting(ConfigOptions.RUN_ID)
        PrintMessage(f"\n<<<<<<<<<<<<<<<< Automated Test run; runId: '{runId}' - complete {passRateMessage}!>>>>>>>>>>>>>>>>\n")

    def _printUsedLibraryVersions(self):
        PrintMessage(f"Python version: {platform.python_version()}")
        PrintMessage(f"Sys version: {sys.version_info}")

    def _printConfiguration(self):
        PrintMessage(" >>> Configuration setup: ")
        for key, value in self.testContext.settings.items():
            PrintMessage(f"{key}:{value}")

    def _printTestContext(self):
        formatted = f"TestContext configuration: \n{pformat(self.testContext.getPrintable())}"
        PrintMessage(formatted)

    def setRunState(self, runState):
        if self.testContext.getSetting(ConfigOptions.RUN_ID):
            adoRequests = ADORequests(AccessTokenEnum.TEST_PLAN_WRITE_ACCESS_TOKEN)
            adoRequests.updateTestRun(self.testContext.getSetting(ConfigOptions.RUN_ID), runState=runState)

    def createTestRunID(self):
        """
        Create test run if one does not exist.
        This method will get called more than one during run time.
        1. Execute all tests
        2. Execute all failures from 1.
        """
        if self.testContext.getSetting(ConfigOptions.RUN_ID):
            return

        adoRequests = ADORequests(AccessTokenEnum.TEST_PLAN_WRITE_ACCESS_TOKEN)

        testPlanName = adoRequests.getTestPlanName(self.testContext.getSetting(ConfigOptions.TEST_PLAN))
        if Constants.DEFAULT_REGRESSION_FOLDER in self.testContext.getSetting(ConfigOptions.TEST_FOLDER):
            testRunName = f"{testPlanName} - Regression Pack"
        else:
            testRunName = f"{testPlanName} - Legacy QRP"

        runId = adoRequests.createADOTestRun(self.testContext.getSetting(ConfigOptions.TEST_PLAN), testRunName)
        self.testContext.setSetting(ConfigOptions.RUN_ID, runId)

        # this is to set environment variable in ADO Pipelines
        print(f"##vso[task.setvariable variable=TESTRUNID;]{runId}")

    def runInParallel(self, testBuckets, postExecutionCBs=()):
        """
        On bulk test run, test user comes from file path_to_users_file

        :param custom_pool_context: Pool context for multiprocessor execution
        :param path_to_users_file: list of users used in parallel testing, each process runs of a different user
        :param postExecutionCBs: list of callbacks to be executed post test execution i.e. upload results up to magic_repo
        :return:
        """
        self._printTestContext()

        with poolcontext() as pool:
            results = pool.starmap(executeSingleSuiteAndUploadResults,
                                   zip(testBuckets,
                                       itertools.repeat(self.testContext)))
            pool.close()
            pool.join()

        if self.testContext.getSetting(ConfigOptions.RUN_ID):
            TestResultsADOUploader(self.testContext).updateTestRunWithScreenshots()

        results = list(set(itertools.chain.from_iterable(results)))
        self._executePostTestCallbacks(postExecutionCBs)
        self._printMessagePostTest(testBuckets, results)

        return results

    def executeMultiDayTests(self, testIds):
        testsToRunContainer = TestsToRunContainer(self.testContext)

        testBucket: TestBucket = testsToRunContainer.getTestSuiteForMultiDayTests(testIds)
        runResult = self.executeTestsOnDemand(testBucket.testSuiteForExecution)

        return TestsResultsContainer(self.testContext, runResult, testBucket)

    def executeTestsOnDemand(self, unitTestSuite, postExecutionCBs=()):
        """
        Run tests either from test ids or test class names (partial is ok)

        On demand, test user comes from test config i.e. TestRunConfig_dev.json

        :param post_execution_cb:
        :return:
        """
        runResult = None
        runner = unittest.TextTestRunner(stream=sys.stdout)
        runner.resultclass = PyStormTextTestResult
        luf = self.testContext.getSetting(ConfigOptions.LOOP_UNTIL_FAILURE)
        lufCounter = 0

        try:
            while True:
                unitTestSuiteCopy = copy.deepcopy(unitTestSuite)
                runResult = runner.run(unitTestSuiteCopy)

                if not (luf and runResult and runResult.wasSuccessful()):
                    break

                lufCounter += 1

            # Used for zipping up test logs and etc
            for callback in postExecutionCBs:
                tryExecute(callback, self.testContext)

        finally:
            if luf:
                PrintMessage(f"LUF > Test executed successfully '{lufCounter}-times' before failing.")

        return runResult
