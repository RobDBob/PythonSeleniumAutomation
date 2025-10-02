import argparse
import os
from azure.data.tables import TableClient, TableServiceClient
from CommonCode.API.ADORequests import AccessTokenEnum, ADORequests
from CommonCode.API.PowerAutomate.PowerAutomateWrapper import PowerAutomateWrapper


class PowerBIToTeamsNotifications(PowerAutomateWrapper):
    """
    PowerBi Report notification to Teams via PowerAutomate
    """

    POWER_BI_PLF_PYS_WORKSPACE = "f01dda25-ea7e-4501-ade9-204d9ca62ed6"
    POWER_BI_TEST_RESULT_REPORT = "12e30e3f-e3e8-46c1-b5d9-c3a7bfc5c631/c66ed1594cc56df8f550"
    POWER_BI_INDIVIDUAL_REPORT_LINK = "https://app.powerbi.com/groups/{0}/reports/{1}"

    def __init__(self, testRunId):
        self.testRunId = testRunId
        self.azureTablesConnectionString = os.environ.get("RESULT_COLLECTION_CONNECTION_STRING")

        self.powerAutomateURL = os.environ.get("PA_URL_REGRESSION_TEST_RESULTS_NOTIFICATION")

        self.runDetails = ADORequests(AccessTokenEnum.TEST_PLAN_READ_ACCESS_TOKEN).getRunDetails(self.testRunId)

    def getIndividualReportLink(self, authorDisplayName, runId):
        reportURL = PowerBIToTeamsNotifications.POWER_BI_INDIVIDUAL_REPORT_LINK.format(PowerBIToTeamsNotifications.POWER_BI_PLF_PYS_WORKSPACE,
                                                                                       PowerBIToTeamsNotifications.POWER_BI_TEST_RESULT_REPORT)
        return f"{reportURL}?filter=PyStormTestResults/RunId eq '{runId}' and PyStormTestResults/AuthorName eq '{authorDisplayName}'"

    def getTestOwnersGrouppedById(self, tableServiceClient: TableServiceClient):
        """
        returns dict
        key: testOwnerId
        value: {displayName, uniqueName}
        """
        testOwnersTableClient: TableClient = tableServiceClient.get_table_client("TestOwners")
        testOwnerDict = {}
        for testOwner in testOwnersTableClient.list_entities():
            testOwnerDict[testOwner.get("RowKey")] = {"displayName": testOwner.get("displayName"),
                                                      "uniqueName": testOwner.get("uniqueName")}

        return testOwnerDict

    def getTestResultsGroupedByOwnerId(self, tableServiceClient: TableServiceClient):
        queryFilter = f"PartitionKey eq '{self.testRunId}' and outcome eq 'Failed'"
        pythonTestResultsTableClient: TableClient = tableServiceClient.get_table_client("PyStormTestResults")

        testResultsDict = {}
        for failedTestResult in pythonTestResultsTableClient.query_entities(queryFilter):
            if failedTestResult.get("testOwnerId") not in testResultsDict:
                testResultsDict[failedTestResult.get("testOwnerId")] = {"failureCount": 1}
            else:
                testResultsDict[failedTestResult.get("testOwnerId")]["failureCount"] += 1
        return testResultsDict

    def getReportRecipients(self):
        with TableServiceClient.from_connection_string(conn_str=self.azureTablesConnectionString) as tableServiceClient:
            testOwners = self.getTestOwnersGrouppedById(tableServiceClient)
            testResultsByOwnerId = self.getTestResultsGroupedByOwnerId(tableServiceClient)

            return testOwners, testResultsByOwnerId

    def sendTeamsNotification(self):
        allTestOwners, testResultsByOwnerId = self.getReportRecipients()
        if not testResultsByOwnerId:
            print(f"TeamsNotifications > There were no recipients identified to send report to for test run: '{self.testRunId}'")

        for ownerId, testResultsCount in testResultsByOwnerId.items():

            powerBiLink = self.getIndividualReportLink(allTestOwners.get(ownerId).get("displayName"), self.testRunId)
            jsonLoad = {
                "runTitle": f"{self.runDetails.get('name')}",
                "runId": self.testRunId,
                "completionDate": self.runDetails.get("completedDate"),
                "recipientUniqueID": allTestOwners.get(ownerId).get("uniqueName"),
                # "recipientUniqueID": "robert.deringer@aberdeenplc.com",
                "recipientName": allTestOwners.get(ownerId).get("displayName"),
                "resultsData": {
                    "failNumber": testResultsCount.get("failureCount")
                },
                "link": powerBiLink
            }

            print(f"Sending teams notification to to {jsonLoad.get('recipientUniqueID')}, no of failures: {testResultsCount.get('failureCount')}")
            self.sendToPowerAutomateFlow(jsonLoad)


def configureArgumentParser():
    parser = argparse.ArgumentParser(description="Send run notifications to individuals on teams, requires runID")
    parser.add_argument("-runID", dest="RUN_ID", required=True, help="Provide Run Id")

    return parser.parse_args()


if __name__ == "__main__":
    args = configureArgumentParser()

    teamsNotifications = PowerBIToTeamsNotifications(args.RUN_ID)
    teamsNotifications.sendTeamsNotification()
