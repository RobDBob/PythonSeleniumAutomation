from CommonCode.TestExecute import Constants as Const
from CommonCode.TestExecute.CommandLineArgumentsParser import CommandLineArgumentsParser
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.Objects.TestsToRunContainer import TestsToRunContainer
from CommonCode.TestExecute.RunManager import RunManager
from CommonCode.TestExecute.TestContext import Test_Context

if __name__ == '__main__':
    CommandLineArgumentsParser.processArgumentsGroupTestRun(Test_Context)

    with RunManager(Test_Context) as testRunner:
        PrintMessage(Const.START_TEST_EXECUTION.format("Primary"))

        testRunner.testContext.setSetting(ConfigOptions.RUN_HEADLESS, True)

        if not testRunner.testContext.getSetting(ConfigOptions.DRY_RUN):
            testRunner.createTestRunID()

        testsToRunContainer = TestsToRunContainer(testRunner.testContext)
        testBuckets = testsToRunContainer.getTestBuckets()

        results = testRunner.runInParallel(testBuckets, postExecutionCBs=[])

        if results and testRunner.testContext.getSetting(ConfigOptions.RE_RUN_FAILED):
            PrintMessage(Const.START_TEST_EXECUTION.format("Secondary"))
            PrintMessage(f"Re-running {len(results)} of failed tests")

            testRunner.testContext.setSetting(ConfigOptions.THIS_RUN_IS_RE_RUN, True)
            testBuckets = testsToRunContainer.getTestBuckets(results)
            testRunner.runInParallel(testBuckets, postExecutionCBs=[])
