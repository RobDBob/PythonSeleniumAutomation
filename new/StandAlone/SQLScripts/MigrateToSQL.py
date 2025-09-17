import json
import os
from azure.data.tables import TableServiceClient
from sqlalchemy.orm import Session
from StandAlone.Reports.AutomationRunReport.HTMLReportGenerator import JiraWrapper
from StandAlone.Reports.AutomationRunReport.HTMLReportHelper import getJiraTicketStatusAsText
from StandAlone.Reports.TestResultsAzureUploader import ResultRecordTable, createTable, getConnectionDBEngine


class MigrateToSQL:
    def __init__(self):
        self.jiraWrapper = JiraWrapper()

    def uploadToSQL(self, listOfEntries, envName, authorName):
        listOfRecords = []
        for entry in listOfEntries:
            testMetaData = json.loads(entry.get("testMetaData", {}))
            tags: str = ",".join(testMetaData.get("tags", []))
            jiraTicketsStatusText = getJiraTicketStatusAsText(self.jiraWrapper.getJiraTickets(tags))

            record = ResultRecordTable(runid=entry["PartitionKey"],
                                       resultid=entry["adoResultId"],
                                       authorname=authorName,
                                       authoridentity=testMetaData.get("owner", "").get("id", ""),
                                       testcaseid=entry["RowKey"],
                                       testcasename=entry["testCaseName"],
                                       outcome=entry["outcome"],
                                       tags=tags,
                                       jiratickets=jiraTicketsStatusText,
                                       envname=envName)
            listOfRecords.append(record)

        with Session(getConnectionDBEngine()) as session:
            session.add_all(listOfRecords)
            session.commit()

    def extractDataFromAT(self):
        """
        Extract data from azure Table and uploads to azure SQL
        """
        connectionString = os.environ.get("RESULT_COLLECTION_CONNECTION_STRING")

        with TableServiceClient.from_connection_string(conn_str=connectionString) as tableServiceClient:
            envName = "UE1"

            for authorName in ["RoshlinAcharya", "RobertDeringer", "NirmalJ", "DivyaShettyVenkatesh", "ArnabChakraborty", "SujataBehera", "RashmiSiddappa"]:
                tableService = tableServiceClient.get_table_client(f"{envName}{authorName}")
                listOfEntries = tableService.list_entities()

                self.uploadToSQL(listOfEntries, envName, authorName)


if __name__ == "__main__":
    # Code used to migrate data from azure tables to azure sql server - one use, keeping for the record

    createTable()
    MigrateToSQL().extractDataFromAT()
    print(1)
