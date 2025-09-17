from CommonCode.TestExecute.CommandLineArgumentsParser import CommandLineArgumentsParser
from CommonCode.TestExecute.Objects.TestsToRunContainer import TestsToRunContainer
from CommonCode.TestExecute.RunManager import RunManager
from CommonCode.TestExecute.TestContext import Test_Context

if __name__ == '__main__':
    CommandLineArgumentsParser.processArgumentsSingleTestRun(Test_Context)

    with RunManager(Test_Context) as testRunner:
        suite = TestsToRunContainer(testRunner.testContext).getTestSuiteForSerialExecution()
        testRunner.executeTestsOnDemand(suite)
