import json
from datetime import datetime
from CommonCode.HelperFunctions import getTestIdFromTestName
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestHelpers.DateMethods import getFutureWeekdayFromToday, parseSafelyToDateTime
from StandAlone.MultiDayTests import MultiDayConst


class MultiDayTestObjs(list):
    def __init__(self, testInstructions, ledgerData):
        super().__init__()
        self.generateTestObjects(testInstructions, ledgerData)

    def generateTestObjects(self, testInstructions, ledgerData):
        """Reads test instructions & ledger data
        Updates all tests with details
        Updates test context with test ids to execute
        """
        todaysDate = datetime.now()  # .strftime(DATE_TIME_FORMAT)
        testInstruction: dict
        for testInstruction in testInstructions:
            testObj = TestObj(testInstruction)
            matchinLedgerData = [k for k in ledgerData if k[MultiDayConst.PARTITION_KEY] == str(testObj.headerTestId)]
            if matchinLedgerData:
                ledgerDataEntity: dict = matchinLedgerData[0]
                testObj.currentStageTestId = int(ledgerDataEntity[MultiDayConst.TEST_ID])
                testObj.currentStageExecutionDate = parseSafelyToDateTime(matchinLedgerData[0].get(MultiDayConst.EXECUTION_DATE), MultiDayConst.DATE_FORMAT)
                testObj.runId = ledgerDataEntity[MultiDayConst.RUN_ID]
                testObj.testData = json.loads(ledgerDataEntity.get(MultiDayConst.TEST_DATA))
            else:
                testObj.currentStageTestId = testObj.headerTestId
                testObj.currentStageExecutionDate = todaysDate

            # skip ones with execution day other than today
            if testObj.currentStageExecutionDate <= todaysDate:
                PrintMessage(f"Identified test: '{testObj.currentStageTestId}' to execute on '{todaysDate}'")
                self.append(testObj)

    def getTestIdsToExecute(self):
        """Returns test ids for execution
        """
        return [testObj.currentStageTestId for testObj in self]

    def _getResult(self, testId, testResults):
        testResults = [k for k in testResults if getTestIdFromTestName(k[0]._testMethodName) == testId]
        if testResults:
            return testResults[0]
        return False

    def getTestObjByTestId(self, testId):
        matchedTestObj = [k for k in self if testId in k.relatedTestIds]
        if matchedTestObj:
            return matchedTestObj[0]
        return None

# pylint: disable=too-many-instance-attributes


class TestObj:
    headerTestId = None  # main / first test id
    unitTestResult = {}
    runId = None
    currentStageTestId = None  # current stage test id
    nextStageTestId = None
    testData = None
    currentStageExecutionDate: datetime = None
    nextStageExecutionDate: datetime = None

    def __init__(self, testInstructions):
        self.headerTestId: str = testInstructions[MultiDayConst.HEADER_TEST_ID]
        self.testStages: list = testInstructions[MultiDayConst.STAGES]

    def setNextStageTestId(self):
        nextStage = None
        if self.currentStageTestId not in self.relatedTestIds:
            return

        matchingStages = [k for k in self.testStages if k[MultiDayConst.TEST_ID] == self.currentStageTestId]
        if matchingStages:
            nextStage = matchingStages[0][MultiDayConst.STAGE] + 1

        matchingTestId = [k for k in self.testStages if k[MultiDayConst.STAGE] == nextStage]
        if matchingTestId:
            self.nextStageTestId = matchingTestId[0].get(MultiDayConst.TEST_ID)
            self.nextStageExecutionDate = getFutureWeekdayFromToday(matchingTestId[0].get(MultiDayConst.DAY))
        else:
            self.nextStageTestId = ""
            self.nextStageExecutionDate = None

    @property
    def relatedTestIds(self):
        return [k.get(MultiDayConst.TEST_ID) for k in self.testStages]

    @property
    def testOutcomePass(self):
        return self.testErrorMessage is None

    @property
    def testErrorMessage(self):
        if self.unitTestResult:
            return self.unitTestResult.get(MultiDayConst.ERROR_MESSAGE)
        return None
