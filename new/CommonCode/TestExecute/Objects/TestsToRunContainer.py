import itertools
import os
import unittest
from enum import Enum
from CommonCode.API.ADORequests import AccessTokenEnum, ADORequests
from CommonCode.HelperFunctions import getTestIdFromTestName
from CommonCode.TestExecute import TestFuncs
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.Objects.TestBucket import TestBucket
from CommonCode.TestExecute.TestContext import TestContext


class TestFilerEnum(Enum):
    TEST_IDS = 1
    TEST_NAMES = 2
    CLASS_NAMES = 3


class TestsToRunContainer:
    MAIN_TEST_FOLDER = "Tests"
    TEST_FILE_PREFIX = "Tests"

    testCasesWithADOData: dict = None

    def __init__(self, testContext):
        self.testContext: TestContext = testContext
        self.folderToSearch = os.path.join(self.MAIN_TEST_FOLDER, self.testContext.getSetting(ConfigOptions.TEST_FOLDER))

    def _getTestCaseIdAndTestPointID(self, testPoints, testSuiteId, testSuiteName):
        """
        Returns dictionary of { testCaseId: {"testPointId": testPointId, "testSuite": testSuiteId }}
        """
        combo = {}
        for testPoint in testPoints.get("value", []):
            testId = int(testPoint["testCase"]["id"])
            combo[testId] = {"testPointId": testPoint["id"],
                             "testSuiteId": testSuiteId,
                             "testSuiteName": testSuiteName}
        return combo

    def _updateLocalCopyOfADOData(self, localTests):
        """
        update internal list of test cases with ADO Data
        structure:
            {"testPointId": testPoint["id"],
             "testSuiteId": testSuiteId,
             "testSuiteName": testSuiteName}
        """
        testPlan = self.testContext.getSetting(ConfigOptions.TEST_PLAN)
        if self.testCasesWithADOData or not testPlan:
            return

        adoRequests = ADORequests(AccessTokenEnum.TEST_PLAN_READ_ACCESS_TOKEN)
        localSuites = {k.ADO_TEST_SUITE for k in localTests}
        testCasesWithADOData = {}
        for adoSuite in adoRequests.testSuitesGet(testPlan):
            adoSuiteId = adoSuite["id"]
            adoSuiteName = adoSuite["name"]

            if adoSuiteName not in localSuites:
                continue

            PrintMessage(f"Get ADO test data for test suite: '{adoSuiteId}': '{adoSuiteName}'.")
            testPoints = adoRequests.testPointsGet(testPlan, adoSuite["id"])
            testsWithTestPoints = self._getTestCaseIdAndTestPointID(testPoints, adoSuiteId, adoSuiteName)
            testCasesWithADOData.update(testsWithTestPoints)
        self.testCasesWithADOData = testCasesWithADOData

    def _discoverLocalTests(self, filterType: TestFilerEnum = None, expectedIdentifiers: list = None) -> dict:
        loader = unittest.TestLoader()
        loader.testMethodPrefix = 'test_C'
        patternToUse = f"{self.TEST_FILE_PREFIX}*.py"
        allTests = loader.discover(self.folderToSearch, pattern=patternToUse)

        assert not loader.errors, str(loader.errors)

        PrintMessage(f"Discovered {allTests.countTestCases()} tests in folder {self.folderToSearch} "
                     f"with search pattern {patternToUse}")

        testsFlatGen = TestFuncs.flattentTestsSuitesIntoGen(allTests)

        if expectedIdentifiers is None:
            return list(testsFlatGen)

        match filterType:
            case TestFilerEnum.TEST_IDS:
                assert expectedIdentifiers, "expected non empty 'expectedIdentifiers'"
                return [k for k in testsFlatGen if getTestIdFromTestName(k._testMethodName) in expectedIdentifiers]
            case TestFilerEnum.TEST_NAMES:
                assert expectedIdentifiers, "expected non empty 'expectedIdentifiers'"
                return [k for k in testsFlatGen if k._testMethodName in expectedIdentifiers]
            case TestFilerEnum.CLASS_NAMES:
                assert expectedIdentifiers, "expected non empty 'expectedIdentifiers'"
                return [k for k in testsFlatGen if k.__class__.__name__ in expectedIdentifiers]
            case _:
                return list(testsFlatGen)

    def getTestBuckets(self, failedTests=None) -> list[dict]:
        """
        Groupping tests by unitTest class for execution purposes

        test bucket requires:
        - local unitTest class - to execute
        - list of relevant tests & relevant ADO data

        Returns test buckets for parallel test execution
        """
        localTests = self._discoverLocalTests(TestFilerEnum.TEST_NAMES, failedTests)
        if self.testContext.getSetting(ConfigOptions.TEST_PLAN):
            self._updateLocalCopyOfADOData(localTests)

        testBuckets = []

        for _, selectedGroupTests in itertools.groupby(localTests, type):
            filteredTestsSuite = unittest.TestSuite()
            filteredTestsSuite.addTests(selectedGroupTests)
            testBuckets.append(TestBucket(filteredTestsSuite, self.testCasesWithADOData))

        PrintMessage(f"Identified {len(testBuckets)} test buckets for execution")
        return testBuckets

    def getTestSuiteForMultiDayTests(self, testIds):
        localTests = self._discoverLocalTests(TestFilerEnum.TEST_IDS, testIds)
        if self.testContext.getSetting(ConfigOptions.TEST_PLAN):
            self._updateLocalCopyOfADOData(localTests)
        multiDayTestSuite = unittest.TestSuite()
        multiDayTestSuite.addTests(localTests)
        return TestBucket(multiDayTestSuite, self.testCasesWithADOData)

    def getTestSuiteForSerialExecution(self):
        suite = unittest.TestSuite()
        if self.testContext.getSetting(ConfigOptions.TEST_IDS):
            testList = self._discoverLocalTests(TestFilerEnum.TEST_IDS, self.testContext.getSetting(ConfigOptions.TEST_IDS))
            suite.addTests(testList)

        elif self.testContext.getSetting(ConfigOptions.TEST_CLASS_NAMES):
            testList = self._discoverLocalTests(TestFilerEnum.CLASS_NAMES, self.testContext.getSetting(ConfigOptions.TEST_CLASS_NAMES))
            for _, selectedGroupTests in itertools.groupby(testList, type):
                suite.addTests(selectedGroupTests)

        return suite
