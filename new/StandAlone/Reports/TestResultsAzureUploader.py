import argparse
import os
import requests
from azure.data.tables import TableServiceClient
from CommonCode.API import APIConstants
from CommonCode.API.ADORequests import AccessTokenEnum, ADORequests
from CommonCode.TestExecute.Logging import PrintMessage
from StandAlone.Reports.AutomationRunReport.HTMLReportGenerator import JiraWrapper
from StandAlone.Reports.AutomationRunReport.HTMLReportHelper import getJiraTicketStatusAsText


class TestResultsAzureUploader:
    """
    used to upload test results to azure tables
    """
    # dict to keep all test owners up to date in azure tables
    _testOnwers = {}

    def __init__(self, runId):
        self.runId = runId
        self.jiraWrapper = JiraWrapper()
        self.azureTablesConnectionString = os.environ.get("RESULT_COLLECTION_CONNECTION_STRING")
        self.refreshPyStormPowerBiDataSetURL = os.environ.get("REFRESH_POWERBI_TEST_REPORT_DATASET_URL")

    def _getTagsFromTestResultComment(self, testComment: str) -> list[str]:
        """
        Splits tags from test case comment section
        """
        comments = testComment.split("Tags")
        if len(comments) > 1:
            return comments[1]
        return ""

    def _updateResultsTable(self, tableServiceClient: TableServiceClient, nonPasedTests: list[dict]):
        pythonTestResultsTableClient = tableServiceClient.create_table_if_not_exists("PyStormTestResults")

        adoTestResult: dict
        for adoTestResult in nonPasedTests:
            self._updateOwnersObj(adoTestResult.get("owner"))

            tags: str = self._getTagsFromTestResultComment(adoTestResult.get("comment", ""))
            jiraTicketsStatusText = getJiraTicketStatusAsText(self.jiraWrapper.getJiraTicketsStatuses(tags), delimiter=", ")

            myEntity = {
                "PartitionKey": str(self.runId),
                "RowKey": str(adoTestResult.get("id")),
                "testCaseName": adoTestResult.get("testCase", {}).get("name"),
                "outcome": adoTestResult.get("outcome"),
                "jiratickets": jiraTicketsStatusText,
                "testOwnerId": adoTestResult.get("owner", {}).get("id"),
                "testPointId": adoTestResult.get("testPoint", {}).get("id"),
                "testCaseId": adoTestResult.get("testCase", {}).get("id")
            }

            pythonTestResultsTableClient.upsert_entity(myEntity)

    def _updateRunTable(self, tableServiceClient: TableServiceClient, runDetails: dict):
        pythonTestRunsTableClient = tableServiceClient.create_table_if_not_exists("PyStormTestRuns")

        runEntity = {
            "PartitionKey": runDetails.get("name"),
            "RowKey": self.runId
        }
        pythonTestRunsTableClient.upsert_entity(runEntity)

    def _updateUsersAzureTable(self):
        tableName = "TestOwners"
        with TableServiceClient.from_connection_string(conn_str=self.azureTablesConnectionString) as tableServiceClient:
            testOwnersTableClient = tableServiceClient.create_table_if_not_exists(tableName)

            for testOwnerId, testOwnerValue in self._testOnwers.items():
                myEntity = {
                    "PartitionKey": "TestAuthors",
                    "RowKey": testOwnerId,
                    "displayName": testOwnerValue.get("displayName"),
                    "uniqueName": testOwnerValue.get("uniqueName")
                }

                testOwnersTableClient.upsert_entity(myEntity)

    def _updateOwnersObj(self, owner: dict):
        """
        Method to keep owners up to date in azure table TestOwners
        """
        if owner.get("id") not in self._testOnwers:
            self._testOnwers[owner.get("id")] = owner

    def uploadRunTestResultsToAzureTable(self):
        """
        Retrives test results for current test run
        Uploads to azure table entity
        """
        PrintMessage("uploadRunTestResultsToAzureTable >> Start")
        runDetails = ADORequests(AccessTokenEnum.TEST_PLAN_READ_ACCESS_TOKEN).getRunDetails(self.runId)
        nonPasedTests = ADORequests(AccessTokenEnum.TEST_PLAN_READ_ACCESS_TOKEN).getTestResultsForTestRun(
            self.runId, filterByOutcomes=[APIConstants.TEST_OUTCOME_FAILED, APIConstants.TEST_OUTCOME_BLOCKED])

        with TableServiceClient.from_connection_string(conn_str=self.azureTablesConnectionString) as tableServiceClient:
            self._updateResultsTable(tableServiceClient, nonPasedTests)
            self._updateRunTable(tableServiceClient, runDetails)

        self._updateUsersAzureTable()

        PrintMessage("uploadRunTestResultsToAzureTable >> End")

    def refreshPowerBIDataSet(self):
        requests.post(url=self.refreshPyStormPowerBiDataSetURL, timeout=60)


def configureArgumentParser():
    parser = argparse.ArgumentParser(description="Upload test results to Azure Tables. Provude RunId")
    parser.add_argument("-runID", dest="RUN_ID", required=True, help="Provide Run Id")

    return parser.parse_args()


if __name__ == "__main__":
    args = configureArgumentParser()

    obj = TestResultsAzureUploader(args.RUN_ID)
    obj.uploadRunTestResultsToAzureTable()
    obj.refreshPowerBIDataSet()
