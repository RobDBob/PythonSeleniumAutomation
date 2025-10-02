import math
import os
import sys
from datetime import datetime, timedelta, timezone
import numpy
from CommonCode.API import APIConstants
from CommonCode.API.ADORequests import AccessTokenEnum, ADORequests
from CommonCode.API.Jira.JiraServiceWrapper import JiraWrapper
from CommonCode.TestExecute.Logging import PrintMessage

PROJECT_URL = "https://aamdev.visualstudio.com/Platform%20Transformation"


class HTMLReportGenerator:
    API_LIMIT = 200

    def __init__(self, testRunId):
        self.workItemsADORequests = ADORequests(AccessTokenEnum.WORK_ITEM_READ_ACCESS_TOKEN)
        self.testPlanADORequests = ADORequests(AccessTokenEnum.TEST_PLAN_READ_ACCESS_TOKEN)

        self.jiraWrapper = JiraWrapper()

        self.testRunId = testRunId
        self.runDetails: dict = self.testPlanADORequests.getRunDetails(testRunId)
        self.testResultsForCurrentRun = self.testPlanADORequests.getTestResultsForTestRun(
            testRunId, filterByOutcomes=[APIConstants.TEST_OUTCOME_FAILED, APIConstants.TEST_OUTCOME_BLOCKED])

        self._historicTestResults = []

    def getWorkItemsDetails(self, testResults):
        workItemIds = [k.get("testCase", {}).get("id") for k in testResults]
        workItemIdsChunks = numpy.array_split(workItemIds, math.ceil(len(workItemIds) / self.API_LIMIT))
        allWorkItems = []

        for workItemIdsChunk in workItemIdsChunks:
            workItems = self.workItemsADORequests.getWorkItemsByIDs(workItemIdsChunk)
            allWorkItems.extend(workItems)

        return allWorkItems

    def getTestCountsForOutcome(self, outcome):
        """
        Retrieves the number of failures per test within the last week for a given test plan ID.
        """
        # Count failures per test case
        testCountForOutcome = {}
        for result in self.historicTestResults:
            if result.get("outcome") == outcome:
                testCaseId = result.get("testCase", {}).get("id")
                testCountForOutcome[testCaseId] = testCountForOutcome.get(testCaseId, 0) + 1

        return testCountForOutcome

    def getDataForHTMLReport(self):
        runTitle: str = self.runDetails.get("name", "")
        runTitleTrimmed = runTitle.replace(" ", "").replace("-", "")

        reportData = {"urlTestRun": self.runDetails.get("webAccessUrl"),
                      "runName": self.runDetails.get("name")}

        filteredTestResultForCurrentRun = [k for k in self.testResultsForCurrentRun if k["outcome"] in ["Failed", "Blocked"]]

        if len(filteredTestResultForCurrentRun) == 0:
            PrintMessage("getDataForReport > No failed or bloked results found")
            return reportData, runTitleTrimmed

        workItems = self.getWorkItemsDetails(filteredTestResultForCurrentRun)
        testCountForFailed = self.getTestCountsForOutcome("Failed")
        testCountForBlocked = self.getTestCountsForOutcome("Blocked")

        failedTests = []
        blockedTests = []
        for testResult in filteredTestResultForCurrentRun:
            testCaseId = testResult.get("testCase", {}).get("id")
            testCaseName = testResult.get("testCase", {}).get("name")
            workItemDetails = [k for k in workItems if k["id"] == int(testCaseId)]
            assert workItemDetails, f"not found work item details for test case id: '{testCaseId}'"
            testPoint = testResult.get("testPoint", {}).get("id")

            tags: str = workItemDetails[0].get("fields", {}).get("System.Tags", "")

            entity = {
                "testCaseId": testCaseId,
                "testCaseName": testCaseName,
                "author": workItemDetails[0].get("fields", {}).get("System.AssignedTo", {}).get("displayName", ""),
                "tags": tags,
                "jiraIssueStatuses": self.jiraWrapper.getJiraTicketsStatuses(tags),
                "urlTestCase": f"{PROJECT_URL}/_workitems/edit/{testCaseId}",
                "urlResult": f"{PROJECT_URL}/_testManagement/runs?runId={self.testRunId}&_a=resultSummary&resultId={testResult.get('id')}",
                "urlExecutionHistory": f"{PROJECT_URL}//_testPlans/_results?testCaseId={testCaseId}&contextPointId={testPoint}",
                "failCount": testCountForFailed.get(testCaseId, 0),
                "blockedCount": testCountForBlocked.get(testCaseId, 0)
            }
            if testResult.get("outcome") == "Failed":
                failedTests.append(entity)
            if testResult.get("outcome") == "Blocked":
                blockedTests.append(entity)

        reportData["failedTests"] = sorted(failedTests, key=lambda item: item["author"])
        reportData["blockedTests"] = sorted(blockedTests, key=lambda item: item["author"])
        return reportData, runTitleTrimmed

    @property
    def historicTestResults(self):
        if not self._historicTestResults:
            endDate = datetime.now(timezone.utc)
            startDate = endDate - timedelta(days=6)

            # Fetch historic test results
            dateAgo = endDate - timedelta(weeks=5)
            while startDate > dateAgo:
                self._historicTestResults.extend(self.testPlanADORequests.getHistoricTestResults(
                    planIds=self.runDetails.get("plan", {}).get("id"),
                    runTitle=self.runDetails.get("name", ""),
                    minLastUpdatedDate=f"{startDate.strftime('%Y-%m-%d')}T00:00:00Z",
                    maxLastUpdatedDate=f"{endDate.strftime('%Y-%m-%d')}T23:59:59Z",
                    state="completed"
                ))
                endDate = startDate - timedelta(days=1)
                startDate = endDate - timedelta(days=6)

        return self._historicTestResults


def main(runId):
    testRunFailedTests = HTMLReportGenerator(runId)
    reportData, runTitleTrimmed = testRunFailedTests.getDataForHTMLReport()

    from StandAlone.Reports.AutomationRunReport.HTMLReportHelper import generateReportFailedTests
    generateReportFailedTests(reportData, runId, runTitleTrimmed)


def getRunId():
    if len(sys.argv) < 2:
        runId = os.environ.get("TESTRUNID")

        if runId:
            PrintMessage(f"HTML Report> RunId found in environment variable: TESTRUNID: '{runId}'")

        return runId

    return sys.argv[1]


if __name__ == '__main__':
    runId = getRunId()

    if runId:
        main(runId)
    else:
        PrintMessage("HTML Report> args error, missed run id? Run script as python -m ")
        PrintMessage("HTML Report> Run script as 'python -m StandAlone.Reports.AutomationRunReport.HTMLReportGenerator 2559517'")
