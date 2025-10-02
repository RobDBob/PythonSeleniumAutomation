import json
import os
from time import time
import yaml
from azure.data.tables import TableServiceClient
from CommonCode.API.ADORequests import ADORequests
from CommonCode.API.PowerAutomate.MultiDayTestTeamsNotification import MultiDayTestTeamsNotification
from CommonCode.TestExecute import Constants as Const
from CommonCode.TestExecute.CommandLineArgumentsParser import CommandLineArgumentsParser
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.Objects.TestsResultsContainer import TestsResultsContainer
from CommonCode.TestExecute.RunManager import RunManager
from CommonCode.TestExecute.TestContext import Test_Context, TestContext
from CommonCode.TestExecute.TestResultsADOUploader import TestResultsADOUploader
from StandAlone.MultiDayTests import MultiDayConst
from StandAlone.MultiDayTests.MultiDayTestObjs import MultiDayTestObjs, TestObj

INSTRUCTIONS_FILE_PATH = r"StandAlone\MultiDayTests\MultiDayTestsInstructions.yml"
# TODO: add to log table


class MultiDayTestExecutor:
    LEDGER_TABLE_NAME = "LedgerTracker"
    LOGGER_TABLE_NAME = "TestLogger"

    def __init__(self, testContext: TestContext):
        self.testContext = testContext
        self.testContext.setSetting(ConfigOptions.TEST_FOLDER, Const.DEFAULT_MULTI_DAY_FOLDER)

        self.azureConnectionString = os.environ.get("MULTIDAYTESTS_AZURE_CONNECTION_STRING")

    def _setRunId(self, testObj: TestObj, testPlanName: str, adoRequests: ADORequests):
        if testObj.runId:
            return

        runName = f"MultiDayRun - {testPlanName} - HeadTestId {testObj.headerTestId}"
        testObj.runId = adoRequests.createADOTestRun(self.testContext.getSetting(ConfigOptions.TEST_PLAN), runName)

    def getTestInProgressFromLedger(self):
        """Retrieves multi day test that are already in progress

        Args:
            environmentName (str): target environment

        Returns:
            list: entites containing tests & test stage
        """

        with TableServiceClient.from_connection_string(conn_str=self.azureConnectionString) as tableServiceClient:
            tableClient = tableServiceClient.create_table_if_not_exists(MultiDayTestExecutor.LEDGER_TABLE_NAME)
            return list(tableClient.list_entities())

    def updateLedger(self, allTestObjs):
        """Save test progress

        Args:
            testsToExecute (dict): {MAIN_TEST_ID: headerTestId, CURRENT_STEP_TEST_ID: currentStepTestId}
            runTestResults (_type_): _description_
        """

        with TableServiceClient.from_connection_string(conn_str=self.azureConnectionString) as tableServiceClient:
            tableClient = tableServiceClient.create_table_if_not_exists(MultiDayTestExecutor.LEDGER_TABLE_NAME)

            testObj: TestObj
            for testObj in allTestObjs:
                nextTestId = testObj.nextStageTestId if testObj.nextStageTestId else None
                executionDateText = testObj.nextStageExecutionDate.strftime(MultiDayConst.DATE_FORMAT) if testObj.nextStageExecutionDate else ""

                myEntity = {
                    MultiDayConst.PARTITION_KEY: self.testContext.getSetting(ConfigOptions.ENVIRONMENT),
                    MultiDayConst.ROW_KEY: str(testObj.headerTestId),
                    MultiDayConst.TEST_ID: nextTestId,
                    MultiDayConst.EXECUTION_DATE: executionDateText,
                    MultiDayConst.RUN_ID: testObj.runId,
                    MultiDayConst.TEST_DATA: json.dumps(self.testContext.getSessionTestData(nextTestId))
                }

                # Update leldger for next execution if test was a pass and nextTestId is set
                if testObj.testOutcomePass and nextTestId:
                    tableClient.upsert_entity(myEntity)
                else:
                    PrintMessage(f"Remove ledger entry '{testObj.headerTestId}' to start new journey on next iteration.")
                    tableClient.delete_entity(myEntity)

    def updateLog(self, allMultiDayTestObjs):
        """Save test progress

        Args:
            testsToExecute (dict): {MAIN_TEST_ID: headerTestId, CURRENT_STEP_TEST_ID: currentStepTestId}
            runTestResults (_type_): _description_
        """

        with TableServiceClient.from_connection_string(conn_str=self.azureConnectionString) as tableServiceClient:
            tableClient = tableServiceClient.create_table_if_not_exists(MultiDayTestExecutor.LOGGER_TABLE_NAME)

            testObj: TestObj
            for testObj in allMultiDayTestObjs:
                executionDateText = testObj.currentStageExecutionDate.strftime(MultiDayConst.DATE_FORMAT) if testObj.currentStageExecutionDate else ""
                myEntity = {
                    MultiDayConst.PARTITION_KEY: self.testContext.getSetting(ConfigOptions.ENVIRONMENT),
                    MultiDayConst.ROW_KEY: f"{str(testObj.headerTestId)}_{int(time())}",
                    MultiDayConst.CURRENT_TEST_ID: testObj.currentStageTestId,
                    MultiDayConst.TEST_STAGE_OUTCOME_PASS: testObj.testOutcomePass,
                    MultiDayConst.TEST_STAGE_ERROR: testObj.testErrorMessage,
                    MultiDayConst.NEXT_TEST_ID: testObj.nextStageTestId,
                    MultiDayConst.EXECUTION_DATE: executionDateText,
                    MultiDayConst.RUN_ID: testObj.runId,
                }

                tableClient.upsert_entity(myEntity)

    def updateTestObjAndADOWithTestResults(self, testResultsContainer: TestsResultsContainer, allMultiDayTestObjs: MultiDayTestObjs):
        """
        - Updates test TestObjs with results
        - Updates test runs with results:
         - create run id if does not exists
         - upload result for new test
         - close run id if no more stages

        Args:
            testResultsContainer (TestsResultsContainer): _description_
            allMultiDayTestObjs (MultiDayTestObjs): _description_
        """
        testObj: TestObj
        testResultsADOUploader = TestResultsADOUploader(self.testContext)
        testPlanName = testResultsADOUploader.adoRequestsTestPlan.getTestPlanName(self.testContext.getSetting(ConfigOptions.TEST_PLAN))
        adoResponses = []
        for testObj in allMultiDayTestObjs:
            self._setRunId(testObj, testPlanName, testResultsADOUploader.adoRequestsTestPlan)

            testObj.unitTestResult = testResultsContainer.getTestDataForTestId(testObj.currentStageTestId)
            testObj.setNextStageTestId()

            adoResponses.append(testResultsADOUploader.uploadMultiDayTestResultToADO(testObj))

            if not (testObj.testOutcomePass and testObj.nextStageTestId):
                # Close test run if the current test outcome is FALSE or
                # all tests were executed i.e. there is no next stage test id available
                errorMessage = "Failed test" if not testObj.testOutcomePass else "Passed test"
                testResultsADOUploader.adoRequestsTestPlan.updateTestRun(testObj.runId,
                                                                         runState="Completed",
                                                                         errorMessage=errorMessage)

                if not testObj.testOutcomePass:
                    MultiDayTestTeamsNotification(testObj.runId).sendTeamsNotification(testObj)

        return adoResponses

    def updateTestContextWithTestData(self, allMultiDayTestObjs):
        testObj: TestObj
        for testObj in allMultiDayTestObjs:
            self.testContext.setSessionTestData(testObj.currentStageTestId, testObj.testData)

    def mainStuffRunner(self):
        with RunManager(self.testContext) as testRunner:
            with open(INSTRUCTIONS_FILE_PATH, encoding="utf-8") as fp:
                testInstructions = yaml.load(fp, yaml.Loader)

            allMultiDayTestObjs = MultiDayTestObjs(testInstructions, self.getTestInProgressFromLedger())

            testIdsToExecute = allMultiDayTestObjs.getTestIdsToExecute()
            if not testIdsToExecute:
                PrintMessage("No tests scheduled for execution today.")
                return

            self.updateTestContextWithTestData(allMultiDayTestObjs)

            testResultsContainer = testRunner.executeMultiDayTests(testIdsToExecute)
            self.updateTestObjAndADOWithTestResults(testResultsContainer, allMultiDayTestObjs)
            self.updateLedger(allMultiDayTestObjs)
            self.updateLog(allMultiDayTestObjs)


if __name__ == "__main__":
    CommandLineArgumentsParser.processArgumentsMultiDayTestRun(Test_Context)

    testExecutor = MultiDayTestExecutor(Test_Context)
    testExecutor.mainStuffRunner()
