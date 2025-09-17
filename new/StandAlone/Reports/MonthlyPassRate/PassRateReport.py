import argparse
import os
from datetime import datetime, timedelta
import pandas as pd
from CommonCode.API.ADORequests import AccessTokenEnum, ADORequests
from CommonCode.TestExecute.Logging import PrintMessage
from StandAlone.Reports.MonthlyPassRate import ReportConsts


class PassRateReport:
    def __init__(self, runTitle, daysToFetch):
        self.runTitle = runTitle
        self.daysToFetch = daysToFetch
        self.adoRequestsWorkItems = ADORequests(AccessTokenEnum.WORK_ITEM_READ_ACCESS_TOKEN)
        self.adoRequestsTestPlan = ADORequests(AccessTokenEnum.TEST_PLAN_READ_ACCESS_TOKEN)

    def getTestRunsByTitleAndDates(self):
        """Function to get all test runs with a specific title within a date range"""
        # Due to the limitation that query filter can be set to maximum 7 days, start and end dates are calculated accordingly
        runTitle = self.runTitle
        endDate = datetime.now().date()
        count = self.daysToFetch
        allRuns = []
        while count != 0:
            if count >= 7:
                startDate = endDate - timedelta(7)
                count -= 7
            else:
                startDate = endDate - timedelta(count)
                count = 0
            runDetails = self.adoRequestsTestPlan.getRuns(startDate, endDate, runTitle)
            endDate = endDate - timedelta(7)
            allRuns.extend(runDetails.get("value", []))
        if not allRuns:
            PrintMessage(f"No runs available for the given title {runTitle} for {self.daysToFetch} days")
        return allRuns

    def aggregateTestCaseResults(self, runs):
        """Function to aggregate test results for Test cases"""
        # Dictionary to store test case results: {testCaseId: {'passed': int, 'total': int}}
        testCaseStats = {}

        for run in runs:
            runId = run["id"]
            testResults = self.adoRequestsTestPlan.getTestResultsForTestRun(runId)

            # Loop through each test result in the run
            for result in testResults:
                testCaseId = result.get("testCase", {}).get("id")
                outcome = result.get("outcome")

                # Initialize test case data if not present and increment the total test executions and if outcome is passed, increase the passed count
                if testCaseId not in testCaseStats:
                    testCaseStats[testCaseId] = {"passed": 0, "total": 0}
                    testCaseDetails = self.adoRequestsWorkItems.getWorkItemByID(testCaseId)
                    testCaseStats[testCaseId]["testOwner"] = testCaseDetails.get("fields", {}).get("System.AssignedTo", {}).get("displayName", "")
                testCaseStats[testCaseId]["total"] += 1
                if outcome == "Passed":
                    testCaseStats[testCaseId]["passed"] += 1
        return testCaseStats

    def calculatePassRateForTestCase(self, testCaseStats):
        """Function to calculate the pass rate for each test case"""
        passRates = []

        for testCaseId, stats in testCaseStats.items():
            totalExecutions = stats.get("total", None)
            passedExecutions = stats.get("passed", None)
            passRate = int((passedExecutions / totalExecutions) * 100)

            passRates.append({
                ReportConsts.COLUMN_TEST_CASE_ID: testCaseId,
                ReportConsts.COLUMN_TEST_CASE_OWNER: stats.get("testOwner", None),
                ReportConsts.COLUMN_TOTAL_EXECUTIONS: totalExecutions,
                ReportConsts.COLUMN_PASS_RATE: passRate
            })
        return passRates

    def saveToCSVFile(self, passRates):
        """Generate Excel Report with Pass Rates for the test cases in the given run"""
        os.makedirs(ReportConsts.OUTPUT_FOLDER, exist_ok=True)
        runTitleWithoutSpace = self.runTitle.replace(" ", "")
        todaysDate = datetime.now().date().strftime("%Y%m%d")
        fileName = os.path.join(ReportConsts.OUTPUT_FOLDER, f"{runTitleWithoutSpace}{todaysDate}.csv")
        data = pd.DataFrame(passRates)
        data.to_csv(fileName, index=False)
        print(f"Report Saved to {fileName}")


def configureArgumentParser():
    parser = argparse.ArgumentParser(description="Generate test case pass rate report. Provide Run Title and number of days to fetch run details")
    runTitleHelp = ("Below are possible titles to include for PyStorm:\n"
                    "PyStorm - UE1 Automated Tests - Regression Pack\n"
                    "PyStorm - TE5 Automated Tests - Regression Pack\n"
                    "PyStorm - DE68 Automated Tests - Regression Pack\n"
                    "PyStorm - TE5 Automated Tests - Legacy QRP\n"
                    "PyStorm - UE1 Automated Tests - Legacy QRP\n"
                    "PyStorm - DE68 Automated Tests - Legacy QRP")
    daysToFetchHelp = "Specify the number of days the data has be fetch for(default is 30)"
    parser.add_argument("-runTitle", required=True, help=runTitleHelp)
    parser.add_argument("-daysToFetch", type=int, default=30, help=daysToFetchHelp)
    return parser.parse_args()


def main():
    args = configureArgumentParser()
    passRateReport = PassRateReport(args.runTitle, args.daysToFetch)
    runs = passRateReport.getTestRunsByTitleAndDates()

    if not runs:
        return

    # Aggregate test case results across all runs
    testCaseStats = passRateReport.aggregateTestCaseResults(runs)

    # Calculate pass rate for each test case
    passRates = passRateReport.calculatePassRateForTestCase(testCaseStats)

    # Save results to Excel
    passRateReport.saveToCSVFile(passRates)


if __name__ == "__main__":
    main()
