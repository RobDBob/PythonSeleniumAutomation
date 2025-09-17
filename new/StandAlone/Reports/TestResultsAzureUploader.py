import argparse
import json
import os
import certifi
from azure.data.tables import TableClient, TableServiceClient
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from CommonCode.API.ADORequests import AccessTokenEnum, ADORequests
from CommonCode.TestExecute.CommandLineArgumentsParser import CommandLineArgumentsParser
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.TestContext import Test_Context, TestContext
from StandAlone.Reports.AutomationRunReport.HTMLReportGenerator import JiraWrapper
from StandAlone.Reports.AutomationRunReport.HTMLReportHelper import getJiraTicketStatusAsText

os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()


Base = declarative_base()


class ResultRecordTable(Base):
    __tablename__ = "pystorm_testresults"

    runid = Column(Integer, primary_key=True)
    resultid = Column(Integer, primary_key=True)
    authorname = Column(String)
    authoridentity = Column(String)
    testcaseid = Column(String)
    testcasename = Column(String)
    outcome = Column(String)
    tags = Column(String)
    jiratickets = Column(String)
    envname = Column(String)


def getConnectionDBEngine():
    """
    Assumes machine has ODBC driver installed
    """
    server = 'pystormresults.database.windows.net'
    database = 'TestResults'
    username = 'db_majtek'
    password = os.environ.get("DB_PYSTORM_RESULTS_PASSWORD")
    driver = "ODBC Driver 18 for SQL Server"

    # Create connection string
    connectionString = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver.replace(' ', '+')}"
    return create_engine(connectionString)


def createTable():
    Base.metadata.create_all(getConnectionDBEngine(), checkfirst=True)


class TestResultsAzureUploader:
    """
    used to upload test results to azure tables
    """

    _tableClients = {}

    def __init__(self, testContext: TestContext):
        self.testContext = testContext
        self.jiraWrapper = JiraWrapper()

    def _getTagsFromTestResultComment(self, testComment: str) -> list[str]:
        comments = testComment.split("Tags")
        if len(comments) > 1:
            return comments[1].split(";")
        return []

    def _getTableClient(self, tableServiceClient: TableServiceClient, ownerName: str) -> TableClient:
        if ownerName not in self._tableClients:
            tableName = f"{self.testContext.getSetting(ConfigOptions.ENVIRONMENT)}{ownerName}"
            self._tableClients[ownerName] = tableServiceClient.create_table_if_not_exists(tableName)
        return self._tableClients[ownerName]

    def uploadRunTestResultsToAzureTable(self):
        """
        Retrives test results for current test run
        Uploads to azure table entity

        15/09/25: replaced with upload to SQL, keeping this method for the record
        """
        runId = self.testContext.getSetting(ConfigOptions.RUN_ID)
        failedTests = ADORequests(AccessTokenEnum.TEST_PLAN_READ_ACCESS_TOKEN).getTestResultsForTestRun(runId)

        connectionString = os.environ.get("RESULT_COLLECTION_CONNECTION_STRING")

        with TableServiceClient.from_connection_string(conn_str=connectionString) as tableServiceClient:
            adoResult: dict
            for adoResult in failedTests:
                testMetaData = {
                    "tags": self._getTagsFromTestResultComment(adoResult.get("comment", "")),
                    "owner": adoResult.get("owner")
                }

                myEntity = {
                    "PartitionKey": str(runId),
                    "RowKey": str(adoResult.get("testCase", {}).get("id")),

                    "testCaseName": adoResult.get("testCase", {}).get("name"),
                    "outcome": adoResult.get("outcome"),
                    "completedDate": adoResult.get("completedDate"),
                    "adoResultId": adoResult.get("id"),
                    "testPointId": adoResult.get("testPoint", {}).get("id"),
                    "url": adoResult.get("url"),
                    "testMetaData": json.dumps(testMetaData)
                }

                ownerName = adoResult.get("owner", {}).get("displayName").replace(" ", "")
                self._getTableClient(tableServiceClient, ownerName).upsert_entity(myEntity)

    def uploadRunTestResultsToAzureDB(self):
        """
        Retrives test results for current test run
        Uploads to azure table entity
        """
        createTable()

        runId = self.testContext.getSetting(ConfigOptions.RUN_ID)
        failedTests = ADORequests(AccessTokenEnum.TEST_PLAN_READ_ACCESS_TOKEN).getTestResultsForTestRun(runId)
        envName = self.testContext.getSetting(ConfigOptions.ENVIRONMENT)

        listOfRecords = []
        for adoResult in failedTests:
            tags: str = ",".join(self._getTagsFromTestResultComment(adoResult.get("comment", "")))
            jiraTicketsStatusText = getJiraTicketStatusAsText(self.jiraWrapper.getJiraTickets(tags))
            authorName = adoResult.get("owner", "").get("displayName", "").replace(" ", "")

            record = ResultRecordTable(runid=str(runId),
                                       resultid=adoResult.get("id"),
                                       authorname=authorName,
                                       authoridentity=adoResult.get("owner", "").get("id", ""),
                                       testcaseid=str(adoResult.get("testCase", {}).get("id")),
                                       testcasename=adoResult.get("testCase", {}).get("name"),
                                       outcome=adoResult.get("outcome"),
                                       tags=tags,
                                       jiratickets=jiraTicketsStatusText,
                                       envname=envName)
            listOfRecords.append(record)

        with Session(getConnectionDBEngine()) as session:
            session.add_all(listOfRecords)
            session.commit()


def configureArgumentParser():
    parser = argparse.ArgumentParser(description="Upload test results to Azure Tables. Provide Configuration name and RunId")
    CommandLineArgumentsParser.addArgumentConfigurationFile(parser)
    parser.add_argument("-runID", dest="RUN_ID", required=True, help="Provide Run Id")

    return parser.parse_args()


if __name__ == "__main__":
    args = configureArgumentParser()

    Test_Context.setSetting(ConfigOptions.RUN_ID, args.RUN_ID)
    Test_Context.setSetting(ConfigOptions.CURRENT_CONFIG_NAME, args.CURRENT_CONFIG_NAME)
    Test_Context.updateFromConfigFile()

    obj = TestResultsAzureUploader(Test_Context)
    obj.uploadRunTestResultsToAzureDB()
