import json
from enum import Enum
from os import environ
import requests
from retry import retry
from CommonCode.API import APIConstants
from CommonCode.TestExecute.Logging import PrintMessage

requests.urllib3.disable_warnings()
# Remember! PAT to basic auth: base64.b64encode((":" + pat).encode()).decode(), then authentication: Basic + base64Token


class AccessTokenEnum(Enum):
    WORK_ITEM_READ_ACCESS_TOKEN = 1
    TEST_PLAN_READ_ACCESS_TOKEN = 2
    TEST_PLAN_WRITE_ACCESS_TOKEN = 3


class ADORequests:
    # Basic auth, Personal Access Token: TestPlanAPI, expires on 13/06/2025; TestManagement Read & Write
    orgAPIURL = "https://dev.azure.com/AAMDev/Platform%20Transformation/_apis/{0}"

    def __init__(self, tokenType: AccessTokenEnum):
        self.authorization = f'Basic {self._getAccessToken(tokenType)}'

    def _getAccessToken(self, tokenType: AccessTokenEnum):
        accessToken = environ.get(tokenType.name)
        assert accessToken, f"Expected to get non-empty ADORequests token for token type '{tokenType.name}'"
        return accessToken

    def executeRequest(self, method, url, **kwargs):
        session = requests.Session()
        session.headers.update({"Authorization": self.authorization})
        session.headers.update({"Content-Type": "application/json"})
        session.headers.update({"Accept": "*/*"})
        session.headers.update({"Accept-Encoding": "gzip, deflate, br"})

        kwargs.setdefault("allow_redirects", True)
        kwargs["verify"] = False

        if "params" not in kwargs:
            kwargs["params"] = {}
        kwargs["params"].update({"api-version": "7.1"})

        response = session.request(method, url, **kwargs)
        if not response.ok:
            PrintMessage(f"Request failed to {method}:{url}")
            PrintMessage(f"result: {response.text}")
            PrintMessage(f"Request headers: {session.headers}")
            PrintMessage(f"Request args: {kwargs}")
        return response

    @retry(exceptions=requests.exceptions.ConnectionError, delay=5, tries=3)
    def executeRequestGetResponse(self, method, url, **kwargs):
        response = self.executeRequest(method, url, **kwargs)
        if response.ok:
            return json.loads(response.text)
        return response

    def patchTestResultInTestPlan(self, adoTestPlan, adoTestSuite, testResults):
        """
        https://learn.microsoft.com/en-us/rest/api/azure/devops/testplan/test-point/update?view=azure-devops-rest-7.0

        request object: https://learn.microsoft.com/en-us/rest/api/azure/devops/testplan/test-point/update?view=azure-devops-rest-7.0#testpointupdateparams
        response object: https://learn.microsoft.com/en-us/rest/api/azure/devops/test/results/update?view=azure-devops-rest-7.0&tabs=HTTP#testcaseresult
        """
        PrintMessage(f"Execute: ADORequests > testResult_AddToTestPlan results to test suite : '{adoTestSuite}'.")
        url = ADORequests.orgAPIURL.format(f"testplan/Plans/{adoTestPlan}/Suites/{adoTestSuite}/TestPoint")
        return self.executeRequestGetResponse("PATCH", url, data=json.dumps(testResults))

    def getTestResultsForTestRun(self, testRunId, filterByOutcomes: list = None):
        """
        Return list of results for test unr
        filterByOutcomes: i.e. Failed

        if detailsToInclude is not used max results is capped at 1000

        https://learn.microsoft.com/en-us/rest/api/azure/devops/test/results/list?view=azure-devops-rest-7.1&tabs=HTTP
        """
        PrintMessage(f"Execute: ADORequests > return results to run: '{testRunId}'")
        topLimit = 1000  # this will be different if detailsToInclude is used

        url = ADORequests.orgAPIURL.format(f"test/runs/{testRunId}/results")

        params = {"outcomes": ','.join(filterByOutcomes)} if filterByOutcomes else {}

        jsonResponse: dict = self.executeRequestGetResponse("GET", url, params=params)
        totalResults = jsonResponse.get("value", [])
        if len(totalResults) < topLimit:
            return totalResults

        params.update({"$skip": topLimit})
        while jsonResponse.get("count") == topLimit:
            jsonResponse: dict = self.executeRequestGetResponse("GET", url, params=params)
            totalResults.extend(jsonResponse.get("value"))
            params["$skip"] += topLimit
        return totalResults

    def getRunDetails(self, testRunId):
        """
        https://learn.microsoft.com/en-us/rest/api/azure/devops/test/runs/get-test-run-by-id?view=azure-devops-rest-5.0&tabs=HTTP
        """
        return self.executeRequestGetResponse("GET", ADORequests.orgAPIURL.format(f"test/runs/{testRunId}"))

    def addTestResultsToTestRun(self, testRunId, testCaseResults, apiAction):
        """
        apiAction:
        - POST - add new
        - PATCH - update existing
        Add test results to test Run
        https://learn.microsoft.com/en-us/rest/api/azure/devops/test/results/add?view=azure-devops-rest-7.1&tabs=HTTP#testcaseresult
        """
        PrintMessage(f"Execute: ADORequests > testRun {apiAction} results to run: '{testRunId}'")
        return self.executeRequestGetResponse(apiAction, ADORequests.orgAPIURL.format(f"test/runs/{testRunId}/results"), data=json.dumps(testCaseResults))

    def testRunUpdate(self, testRunId, testRunDetails: dict):
        """
        https://learn.microsoft.com/en-us/rest/api/azure/devops/test/runs/update?view=azure-devops-rest-7.0&tabs=HTTP
        Expectedd details in testRunDetails dictionary are listed within RequestBody section of above document
        """
        PrintMessage("Execute: ADORequests > testRun_Update.")
        url = ADORequests.orgAPIURL.format(f"test/runs/{testRunId}")
        return self.executeRequestGetResponse("PATCH", url, data=json.dumps(testRunDetails))

    def testRunResultsAddAttachment(self, testRunId, resultId, attachment: dict):
        """
        https://learn.microsoft.com/en-us/rest/api/azure/devops/test/attachments/create-test-result-attachment?view=azure-devops-rest-7.0&tabs=HTTP
        {
            "stream" : "base64encoded",
            "fileName": "textAsFileAttachment.png",
            "comment": "Test attachment upload",
            "attachmentType": "GeneralAttachment"
        }
        """
        return self.executeRequestGetResponse("POST",
                                              ADORequests.orgAPIURL.format(f"test/runs/{testRunId}/results/{resultId}/attachments"),
                                              data=json.dumps(attachment))

    def testPointsGet(self, testPlan, testSuite):
        return self.executeRequestGetResponse("GET", ADORequests.orgAPIURL.format(f"test/plans/{testPlan}/suites/{testSuite}/points"))

    def testSuiteGet(self, testPlan, testSuite):
        """
        Returns testSuite with children suites (expand=children) option
        https://learn.microsoft.com/en-us/rest/api/azure/devops/testplan/test-suites/get?view=azure-devops-rest-5.0&tabs=HTTP#suiteexpand
        """
        url = ADORequests.orgAPIURL.format(
            f"testplan/Plans/{testPlan}/suites/{testSuite}?expand=children")
        return self.executeRequestGetResponse("GET", url)

    def testSuitesGet(self, testPlanId):
        """
        Returns testSuite with children suites (expand=children) option
        https://learn.microsoft.com/en-us/rest/api/azure/devops/testplan/test-suites/get?view=azure-devops-rest-5.0&tabs=HTTP#suiteexpand
        """
        PrintMessage(f"Execute: ADORequests > getAllTestSuites for test plan: '{testPlanId}'.")
        url = ADORequests.orgAPIURL.format(f"testplan/Plans/{testPlanId}/suites")
        response = self.executeRequest("GET", url)

        allSuites: list = json.loads(response.text).get("value")

        while response.headers.get("x-ms-continuationtoken"):
            response = self.executeRequest("GET",
                                           url,
                                           params={"continuationToken": response.headers.get("x-ms-continuationtoken")})
            allSuites.extend(json.loads(response.text).get("value"))

        return allSuites

    def getTestPlanDetails(self, testPlanId):
        """
        Returns test plan details
        https://learn.microsoft.com/en-us/rest/api/azure/devops/testplan/test-plans/get?view=azure-devops-rest-5.0&tabs=HTTP#testplan
        """
        return self.executeRequestGetResponse("GET", ADORequests.orgAPIURL.format(f"testplan/plans/{testPlanId}"))

    def getTestPlanName(self, testPlanId):
        testPlanDetails: dict = self.getTestPlanDetails(testPlanId)
        return testPlanDetails.get("name", "")

    def createADOTestRun(self, testPlanId, runName, **kwargs):
        """
        Creates test run, returns run Id
        https://learn.microsoft.com/en-us/rest/api/azure/devops/test/runs/create?view=azure-devops-rest-7.1&tabs=HTTP
        """
        runData = {
            "automated": True,
            "comment": kwargs.get("comment", "testComment"),
            "errorMessage": kwargs.get("errorMessage", "testErrorMessage"),
            "name": runName,
            "plan": {
                "id": testPlanId
            }
        }
        response = self.executeRequestGetResponse("POST", ADORequests.orgAPIURL.format("test/runs"), data=json.dumps(runData))
        if response and isinstance(response, dict):
            return response.get("id")
        return None

    def updateTestRun(self, runId, runState="Completed"):
        """
        Creates test run, returns run Id
        https://learn.microsoft.com/en-us/rest/api/azure/devops/test/runs/create?view=azure-devops-rest-7.1&tabs=HTTP
        Valid states: Unspecified ,NotStarted, InProgress, Completed, Waiting, Aborted, NeedsInvestigation
        """
        runData = {
            "state": runState,
        }
        return self.executeRequestGetResponse("PATCH", ADORequests.orgAPIURL.format(f"test/runs/{runId}"), data=json.dumps(runData))

    def getWorkItemByID(self, workItemID):
        """
        Returns work item details from ADO
        https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/get-work-item?view=azure-devops-rest-7.1&tabs=HTTP#get-work-item
        """
        return self.executeRequestGetResponse("GET", ADORequests.orgAPIURL.format(f"/wit/workitems/{workItemID}"))

    def getWorkItemsByIDs(self, workItemIDs):
        """
        Returns work item details from ADO
        https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/list?view=azure-devops-rest-7.1&tabs=HTTP
        """
        response = self.executeRequestGetResponse("GET", ADORequests.orgAPIURL.format("/wit/workitems"), params={"ids": ','.join(workItemIDs)})
        assert isinstance(response, dict), f"expected dict type, suspect error: '{response.text}'"
        return response.get("value")

    def getRuns(self, minDate, maxDate, runTitle):
        """Get the run IDs for the runs executed within minDate to maxDate with the given runTitle
        """
        return self.executeRequestGetResponse("GET", ADORequests.orgAPIURL.format("test/runs"), params={"minLastUpdatedDate": minDate,
                                                                                                        "maxLastUpdatedDate": maxDate,
                                                                                                        "runTitle": runTitle})

    def getHistoricTestResults(self, **params):
        """
        https://learn.microsoft.com/en-us/rest/api/azure/devops/test/runs/query?view=azure-devops-rest-7.1

        Retrieves historic test results for a given test plan.

        :param testPlanId: ID of the test plan to retrieve results for.
        :param startDate: (Optional) Start date for filtering results (ISO 8601 format: YYYY-MM-DD).
        :param endDate: (Optional) End date for filtering results (ISO 8601 format: YYYY-MM-DD).
        :return: List of test results.
        """
        PrintMessage(f"Execute: ADORequests > getHistoricTestResults with parameters: for test plan: {params}.")

        # Fetch test runs for the test plan
        testRuns = self.executeRequestGetResponse("GET", ADORequests.orgAPIURL.format("test/runs"), params=params)
        if not testRuns or "value" not in testRuns:
            PrintMessage(f"No test runs found for the specified test plan and date range: from {params.get('minLastUpdatedDate')} to {params.get('maxLastUpdatedDate')}")
            return []

        # Collect test results for each test run
        allTestResults = []
        for testRun in testRuns["value"]:
            testRunId = testRun.get("id")
            if testRunId:
                testResults = self.getTestResultsForTestRun(testRunId, filterByOutcomes=[APIConstants.TEST_OUTCOME_FAILED, APIConstants.TEST_OUTCOME_BLOCKED])
                if testResults:
                    allTestResults.extend(testResults)

        return allTestResults
