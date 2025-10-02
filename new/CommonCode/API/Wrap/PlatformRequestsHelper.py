import random
import re
from os import path
from types import SimpleNamespace
from bs4 import BeautifulSoup
from CommonCode.API.BackOffice.BackOfficeHelper import BackOfficeHelper
from CommonCode.API.Objects.Customer import CustomerObj
from CommonCode.API.Objects.Trust.TrustServicingModel import TrustServicingModel
from CommonCode.API.Wrap.Requests.PlatformRequests import PlatformRequests
from CommonCode.API.Wrap.Requests.TrustServicingRequests import TrustServicingRequests
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.TestContext import TestContext
from TestPages.ClientsTabs.IndividualSearchCriteria import IndividualSearchCriteria
from TestPages.ClientsTabs.SearchCriteriaOptions import AccountRole, CustomerStatus


class PlatformRequestsHelper:
    def __init__(self, wrapAPISessionHeaders: dict, testContext: TestContext):
        self.testContext = testContext
        self.wrapAPISessionHeaders = wrapAPISessionHeaders
        self.platformRequests = PlatformRequests(self.wrapAPISessionHeaders, testContext.getSetting(ConfigOptions.SLWRAP_API_URL))

    def getRandomActiveTestCustomer(self, currentPage=20) -> CustomerObj:
        """
        Recursive method
        Returns active account (non prospect)
        """
        searchCriteria = IndividualSearchCriteria()
        searchCriteria.status = CustomerStatus.Active
        searchCriteria.accountRole = AccountRole.Individual
        params = searchCriteria.getAPIQueryParamsAsString(currentPage=currentPage)
        accounts = self.platformRequests.customerSearch(params)

        nonProspectAccounts = [k for k in accounts if not k.get("IsProspect")]
        if nonProspectAccounts:
            testAccount = random.choice(nonProspectAccounts)
            PrintMessage(
                f"PlatformRequestHelper > Using test account: first name: {testAccount.get('FirstName', '')}, last name: {testAccount.get('LastName', '')}",
                inStepMessage=True)
            return CustomerObj(testAccount)

        if currentPage < 20:
            return self.getRandomActiveTestCustomer(currentPage + 1)

        PrintMessage(f"PlatformRequestHelper > Failed to find non prospect account after scouting '{currentPage}'- result pages", inStepMessage=True)
        return None

    def downloadFile(self, url, destinationFilePath):
        dataChunk = 8192
        customHeader = {'Accept-Encoding': 'gzip'}

        with self.platformRequests.executeRequest("GET", url, headers=customHeader) as response:
            with open(destinationFilePath, 'wb') as fd:
                for chunk in response.iter_content(dataChunk):
                    fd.write(chunk)

    def getOpenOrdersBathesForAccount(self, accountNumber):
        """
        Method returns a dictionary of open batches with lists of related open orders
        """
        responseText = self.platformRequests.getClientOrders(accountNumber)

        parsedHTML = BeautifulSoup(responseText, features="html.parser")
        subHeads = parsedHTML.body.find_all("tr", attrs={"class": "sub-head"})
        htmlMatches = []
        for subHead in subHeads:
            descendants = list(subHead.children)
            htmlMatches.extend([str(k) for k in descendants if 'Batch' in str(k)])

        # Find batches
        batchNumbers = []
        for htmlMatch in htmlMatches:
            matchObject = re.search(r"Batch (\d*)", htmlMatch)
            if matchObject:
                batchNumbers.append(matchObject.group(1))

        # Find corresponding orders
        result = {}
        batchNumbers.reverse()
        for batchNumber in batchNumbers:
            orderIds = []
            matches = re.findall(rf"{batchNumber}\.(\d*)", responseText)
            for match in matches:
                if match:
                    PrintMessage(f"PlatformRequestHelper > Found open order: '{match}' for batch: '{batchNumber}'.", inStepMessage=True)
                    orderIds.append(match)
            result[batchNumber] = orderIds

        return result

    def closeAnyOpenOrdersForAccount(self, accountNumber, userNumber):
        """
        Check if there are any open deals for given account via UI
        Make an attempt to close those via API
        Closing via API might fail due to UI and API being out of sync, in such case retry until certain
        """
        openOrderBatches = self.getOpenOrdersBathesForAccount(accountNumber)
        if not openOrderBatches:
            PrintMessage(f"PlatformRequestHelper > No open orders found for account number: '{accountNumber}'", inStepMessage=True)
            return

        PrintMessage(f"PlatformRequestHelper > Found {len(openOrderBatches)}-open order for account number: '{accountNumber}'", inStepMessage=True)
        boUserName, boUserPassword = self.testContext.testUsers.getBOUserByNumber(userNumber)
        backOfficeHelper = BackOfficeHelper(self.testContext.getSetting(ConfigOptions.BACK_OFFICE_URL), boUserName, boUserPassword)
        backOfficeHelper.closeAllOrders(openOrderBatches)

    def cancelPaymentWithdrawal(self, accountNumber, regularWithdrawalID):
        """
        Cancels regular withdrawal as per test case C1390745
        Code will need update to work with other cases
        """
        # to kick off session
        getEntriesResponse = self.platformRequests.getCashEntries(accountNumber)

        parsedHTML = BeautifulSoup(getEntriesResponse, features="html.parser")
        params = {"claccountid": accountNumber, "RegularWithdrawalID": regularWithdrawalID}
        data = {
            "claccountId": accountNumber,
            "subclaccountid": accountNumber,
            "actionType": "setupcancel",
            "cashid": regularWithdrawalID,
            "InstructionType": "All",
            "__RequestVerificationToken": parsedHTML.body.find("input", attrs={"id": "__RequestVerificationToken"})["value"],
            "RandomString": parsedHTML.body.find("input", attrs={"id": "RandomString"})["value"]
        }
        responseText = self.platformRequests.regularWithdrawal("POST", data, params)

        parsedHTML = BeautifulSoup(responseText, features="html.parser")
        data = {
            "claccountId": accountNumber,
            "actionType": "cancel",
            "RegularWithdrawalID": regularWithdrawalID,
            "subclaccountid": accountNumber,
            "webauditlogid": parsedHTML.body.find("input", attrs={"id": "webauditlogid"})["value"],
            "__RequestVerificationToken": parsedHTML.body.find("input", attrs={"id": "__RequestVerificationToken"})["value"],
            "RandomString": parsedHTML.body.find("input", attrs={"id": "RandomString"})["value"]
        }

        return self.platformRequests.regularWithdrawal("POST", data)

    def getAccountsFromClientId(self, clientId):
        """
        Gets account and subaccount from API
        Transforms JSON into python objects
        Expected format is:

        AccountName: 'random_DYYtM'
        AccountServicePropositionId: 2
        AccountStatus: 0
        AdviserCode: 'BATEJB1'
        AdviserName: 'BATE-3/FV25-BATEJB1'
        ClientType: 2
        ClosedDate: None
        Company: 'BATE'
        CompanyAdvCode: '3/FV25'
        CompanyName: 'Bateman Asset Management'
        Discretionary: True
        FeeStructure: 'AdviserCharging'
        GoPaperless: False
        HeadClAccountId: 'WP1803809'
        HierarchyId: '001-0002180085'
        InceptionDate: '2023-11-16T00:00:00'
        InvestorType: 4
        RestrictActivities: None
        SubAccounts: [
            'ClAccountId': 'WP1803809-003'
            'HierarchyId': '000-0002180090'
            'SubAccountType': 3
            'Company': 'BATE'
            'ProductDisplayName': 'ISA Stocks & Shares'
            'InceptionDate': '2023-11-16T00:00:00'
            'Status': 0
            'IsAvailable':True
        ]
        Data might be different depending on supplied clientId parameter
        """
        responseListJson = self.platformRequests.getCustomerAccount(clientId)
        accountsObjs = []
        for dictAccount in responseListJson:
            subAccountObjs = []
            objAccount = SimpleNamespace(dictAccount)
            for dictSubAccount in objAccount.SubAccounts:
                subAccountObjs.append(SimpleNamespace(dictSubAccount))
            objAccount.SubAccounts = subAccountObjs
            accountsObjs.append(objAccount)
        return accountsObjs

    def getCustomerId(self, accountNumber, orgName):
        orgResults = self.platformRequests.organizationSearch(accountNumber, orgName)
        assert orgResults.get("TotalNumberOfResults", 0) > 0, f"Expected non-zero results from organization search for '{accountNumber}', '{orgName}'"
        return orgResults.get("PageOfResults")[0].get("CustomerId")

    def addRandomBeneficiaryToOrganization(self, accountNumber, orgName):
        """
        WIP very much
        Adds random beneficiary
        New share of trust is equal split
        """
        customerId = self.getCustomerId(accountNumber, orgName)
        trustRequests = TrustServicingRequests(self.wrapAPISessionHeaders, self.testContext.getSetting(ConfigOptions.SLWRAP_API_URL))
        trustServicingModel: TrustServicingModel = trustRequests.getCustomerTrustServicingModel(customerId)

        breq = trustServicingModel.generateNewTrustBeneficiaryJson()

        return trustRequests.addBeneficiary(breq)

    def removeAdditionalBeneficiaries(self, accountNumber, orgName):
        """
        Remove beneficiary,
        reason for deletion: ?
        spread share onto others
        """
        customerId = self.getCustomerId(accountNumber, orgName)
        trustRequests = TrustServicingRequests(self.wrapAPISessionHeaders, self.testContext.getSetting(ConfigOptions.SLWRAP_API_URL))
        trustServicingModel: TrustServicingModel = trustRequests.getCustomerTrustServicingModel(customerId)

        for currentBeneficiary in trustServicingModel.organization.getAdditionalBeneficiaries():
            breq = trustServicingModel.generateRemoveTrustBeneficiaryJson(currentBeneficiary.sourceJson)
            trustRequests.deleteBeneficiary(breq)

    def downloadDocumentsFromLoadstore(self, instructions):
        """
        Downloads document from loadstore
        instructions = [{"url": "url", "destination": "destination"}]
        """
        PrintMessage(f"downloadDocumentsFromLoadstore > Downloading: {instructions} ", inStepMessage=True)
        downloadedFiles = []
        for instruction in instructions:
            url = f"{self.testContext.getSetting(ConfigOptions.SLWRAP_API_URL)}/{instruction['url']}"
            requestResult = self.platformRequests.executeRequest("GET", url)
            destinationFilePath = path.join(self.testContext.testDownloadFolder, instruction["docFileName"])
            with open(destinationFilePath, "wb") as f:
                f.write(requestResult.content)
            downloadedFiles.append(destinationFilePath)
            PrintMessage(f"downloadDocumentsFromLoadstore > Downloaded: '{destinationFilePath}'", inStepMessage=True)
        return downloadedFiles

    def _getRejectAuthProcessesData(self, parsedHTML, trustProcess, trustNewBusinessProcess, trustProcessAccount, rejectTrust):
        ignoreLastEntries = 20

        reTrustProcess = re.compile(f"{trustProcess}.*")
        reTrustNewBusinessProcess = re.compile(f"{trustNewBusinessProcess}.*")
        reTrustProcessAccount = re.compile(f"{trustProcessAccount}.*")

        sectionElement = parsedHTML.findParent().find_next_sibling("div", {"class": "table-scrollable mb-30"})

        requestData = {}
        allRows = sectionElement.find("tbody").find_all("tr")
        for trElement in allRows[:-ignoreLastEntries]:
            customerTrustProcess = trElement.find("input", {"name": reTrustProcess})
            customerTrustNewBusinessProcess = trElement.find("input", {"name": reTrustNewBusinessProcess})
            customerTrustProcessAccount = trElement.find("input", {"name": reTrustProcessAccount})

            processId = re.search(rf"{trustProcess}(\d*)", customerTrustProcess["id"]).group(1)
            trustProcessToRemove = {
                f"{trustProcess}{processId}": customerTrustProcess["value"],
                f"{trustNewBusinessProcess}{processId}": customerTrustNewBusinessProcess["value"],
                f"{trustProcessAccount}{processId}": customerTrustProcessAccount["value"],
                f"{rejectTrust}{processId}": "on"
            }

            requestData.update(trustProcessToRemove)

        PrintMessage(f"_getRejectAuthProcessesData > Found {len(requestData)} {trustProcess} entries to reject", inStepMessage=True)
        return requestData

    def rejectAllAuthoriseProcesses(self):
        """
        Rejects all trust processes
        Retrieves all trust and client trust unauthorised processes, then proceeds to rejecting them
        All with exception of 100 most recent (at the bottom of the page) are removed to accommodate any current actions in progress
        """

        authProcessesResponse = self.platformRequests.executeAuthoriseProcessesRequest("GET")
        parsedHTML = BeautifulSoup(authProcessesResponse, features="html.parser")
        data = {
            "__VIEWSTATE": parsedHTML.body.find("input", attrs={"name": "__VIEWSTATE"})["value"],
            "__VIEWSTATEGENERATOR": parsedHTML.body.find("input", attrs={"name": "__VIEWSTATEGENERATOR"})["value"],
            "__RequestVerificationToken": parsedHTML.body.find("input", attrs={"name": "__RequestVerificationToken"})["value"],
            "RandomString": parsedHTML.body.find("input", attrs={"name": "RandomString"})["value"],
            "actiontype": "reject",
            "claccountid": parsedHTML.body.find("input", attrs={"name": "claccountid"})["value"],
            "sortCol": parsedHTML.body.find("input", attrs={"name": "sortCol"})["value"],
            "sortDirection": parsedHTML.body.find("input", attrs={"name": "sortDirection"})["value"],
            "helptagid": parsedHTML.body.find("input", attrs={"name": "helptagid"})["value"],
            "maxclientactivitiesrequests": parsedHTML.body.find("input", attrs={"name": "maxclientactivitiesrequests"})["value"],
            "maxtrustauthorisations": parsedHTML.body.find("input", attrs={"name": "maxtrustauthorisations"})["value"],
        }

        data.update(self._getRejectAuthProcessesData(parsedHTML.body.find("h2", text="Authorise Customer Trust Processes"),
                                                     "customertrustprocess",
                                                     "customertrustnewbusinessprocess",
                                                     "customertrustprocessaccount",
                                                     "rejectcustomertrust"))

        data.update(self._getRejectAuthProcessesData(parsedHTML.body.find("h2", text="Authorise Trust Processes"),
                                                     "trustprocess",
                                                     "trustnewbusinessprocess",
                                                     "trustprocessaccount",
                                                     "rejecttrust"))

        self.platformRequests.executeAuthoriseProcessesRequest("POST", data)
