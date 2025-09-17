import argparse
import csv
import os
import re
from CommonCode.API import APIConstants
from CommonCode.API.Wrap.AccountRequestsHelper import AccountRequestsHelper
from CommonCode.CustomExceptions import APIException
from CommonCode.TestExecute.BrowserSetup import BrowserSetup
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.TestContext import Test_Context
from TestPages.PlatformLoginPage import PlatformLoginPage


class FindAccount:
    accountAPIRequestsHelper = None
    testContext = None

    def __init__(self, environment, userName, userPassword):
        self.userName = userName
        self.userPassword = userPassword
        self.environment = environment
        self._setTestContext()

        self.localAccounts = self._getAllLocalAccounts()
        self.goldenCasesAccounts = self._getAllGoldenCasesAccounts()

    def _setTestContext(self):
        self.testContext = Test_Context
        self.testContext.setSetting(ConfigOptions.CURRENT_CONFIG_NAME, f"{self.environment}chromeTestServer")
        self.testContext.setSetting(ConfigOptions.RUN_HEADLESS, True)
        self.testContext.updateFromConfigFile()

    def _getAllLocalAccounts(self):
        """
        Retruns all WP accounts used in tests
        """
        path = f"TestData\\{self.environment}"
        yamlFiles = [os.path.join(root, name)
                     for root, dirs, files in os.walk(path)
                     for name in files
                     if name.endswith((".yml", ".yaml"))]
        allAccounts = []
        for yamlFile in yamlFiles:
            with open(yamlFile, "r", encoding="utf-8") as f:

                fileContent = f.read()
                matches = re.findall(r"(WP\d{7})", fileContent, re.IGNORECASE)
                if matches:
                    allAccounts.extend(matches)
        return allAccounts

    def _getAllGoldenCasesAccounts(self):
        goldenCasesFilePath = f"TestData\\TestAccounts\\GoldenCases{self.environment}.csv"
        if not os.path.exists(goldenCasesFilePath):
            print("issue, golden cases file does not exists")

        goldenCasesAccounts = []
        with open(goldenCasesFilePath, "r", encoding="utf-8") as f:
            # pylint: disable = expression-not-assigned
            [goldenCasesAccounts.append(k[0]) for k in csv.reader(f)]
        return goldenCasesAccounts

    def _checkExpectedSubAccountsTypeAreMet(self, expectedSubAccountType, customerId):
        actualCustomerDetails = self.accountAPIRequestsHelper.platformRequests.getCustomerAccount(customerId)
        for actualAccount in actualCustomerDetails:
            actualSubAccounts = [actualSubAccount["SubAccountType"] for actualSubAccount in actualAccount["SubAccounts"]]
            if set(actualSubAccounts).intersection(expectedSubAccountType):
                return actualAccount
        return None

    def _checkProductValuationSummaryDetailsAreMet(self, instruction, account):
        subAccountsHierarchyIds = [k["HierarchyId"] for k in account["SubAccounts"] if k["SubAccountType"] == instruction["AccountType"]]
        summaryDetails = self.accountAPIRequestsHelper.getProductValuationSummaryDetails(account["HierarchyId"], subAccountsHierarchyIds)
        matchingSubAccounts = []
        for summaryDetail in summaryDetails["Products"]:
            outCome = True
            if summaryDetail["ProductType"] not in instruction["ExpectedProductTypes"]:
                return None

            if instruction.get("TotalValueGreaterThan"):
                outCome = summaryDetail.get("TotalValue", {}).get("Amount", 0) > instruction["TotalValueGreaterThan"]
            else:
                outCome = True

            # to add more checks

            if outCome:
                matchingSubAccounts.append(summaryDetail)
        return matchingSubAccounts

    def _checkInvestmentDetailsAreMet(self, instruction, actualSubAccount):
        if actualSubAccount["ProductType"] == APIConstants.PP_ACCOUNT_TYPE:
            investmentsDetail = self.accountAPIRequestsHelper.getPortFolioInvestment(actualSubAccount)
        elif actualSubAccount["ProductType"] == APIConstants.ISA_ACCOUNT_TYPE:
            # investmentsDetail = self.accountAPIRequestsHelper.getPortFolioInvestment(subAccount)
            investmentsDetail = None
        else:
            investmentsDetail = None

        if not investmentsDetail:
            return None

        # WE NEED ONE MATCHING SUB ACCOUNT
        for investmentDetail in investmentsDetail:

            # check investments to avoid
            for investmentToAvoid in instruction["InvestmentsToAvoid"]:
                if investmentDetail.get(investmentToAvoid):
                    return None

            if instruction.get("IndividualInvestmentsPresent"):
                if len(investmentDetail.get("IndividualInvestments", ())) > 0:
                    # matchingSubAccounts.append(investmentDetail)
                    return investmentDetail["ClAccountId"].split("-")[0]
            else:
                return investmentDetail["ClAccountId"].split("-")[0]

        return None

    def filterOutUsedAccounts(self, platformAccounts):
        """
        get accounts that are not used in test framework and are of expected account type i.e. individual
        """
        unusedAccounts = [k for k in platformAccounts if not (k["ClAccountId"] in self.localAccounts or k["ClAccountId"] in self.goldenCasesAccounts)
                          and k["AccountType"] == instructions["AccountType"]]
        return unusedAccounts

    def findPotentialAccountsForInitialNumber(self, instructions, initialAccountNumber, numberOfAccountsToFind):
        """
        Current implementation works of ONE subaccount
        """
        platformAccounts = self.accountAPIRequestsHelper.getWPAccounts(initialAccountNumber)
        print(f"\nVeryfing {len(platformAccounts)}-accounts with for initial account number: {initialAccountNumber}", end="")
        filteredAccounts = self.filterOutUsedAccounts(platformAccounts)

        potentialAccounts = []
        for filteredAccount in filteredAccounts:
            print(".", end="")
            account = self._checkExpectedSubAccountsTypeAreMet(instructions["ExpectedSubAccountTypes"], filteredAccount["CustomerId"])
            if not account:
                continue

            subAccounts = self._checkProductValuationSummaryDetailsAreMet(instructions, account)
            if not subAccounts:
                continue

            for subAccount in subAccounts:
                wpAccount = self._checkInvestmentDetailsAreMet(instructions, subAccount)
                if wpAccount:
                    openOrders = self.accountAPIRequestsHelper.getOpenOrdersBathesForAccount(wpAccount)

                    if len(openOrders) < 1:
                        potentialAccounts.append(wpAccount)

            if len(potentialAccounts) >= numberOfAccountsToFind:
                break

        return potentialAccounts

    def setAPISession(self):
        driver = BrowserSetup(self.testContext).setup()
        platform = PlatformLoginPage(driver).performLogin(self.userName, self.userPassword)
        self.accountAPIRequestsHelper = AccountRequestsHelper(platform.webdriver.apiSessionHeaders, self.testContext)

    def accountSearchMain(self, instructions):
        self.setAPISession()
        initialAccountNumber = instructions["initialAccountNumber"]
        numberOfAccountsTofind = instructions["NumberOfAccountsToFind"]
        potentialAccounts = []
        while len(potentialAccounts) <= numberOfAccountsTofind:
            try:
                potentialAccounts.extend(self.findPotentialAccountsForInitialNumber(instructions,
                                                                                    initialAccountNumber,
                                                                                    numberOfAccountsTofind - len(potentialAccounts)))
            except APIException:
                pass

            initialAccountNumber += 2

        return potentialAccounts


def configureArgumentParser():
    parser = argparse.ArgumentParser(description="Performs account search. Runs cross check against accounts used in automation and golden cases.")
    initialAccontHelp = "Starting point for account search"
    envNameHelp = "Specify envirionment to run search against"
    parser.add_argument("-initialAccountNumber", required=True, type=int, help=initialAccontHelp)
    parser.add_argument("-envName", required=True, help=envNameHelp)
    return parser.parse_args()


if __name__ == "__main__":
    # COMMAND LINE TO TRIGGER: python -m StandAlone.FindAccount
    # USE:
    # python -m StandAlone.FindAccount -initialAccountNumber 1805 -envName ue1

    # Will be only searching for WP numbers
    # SubAccountType:
    # PP: 1
    # ISA : 3
    # Cash Account: 14

    # AccountType
    # Individual: 1
    # Joint: 2
    # Trust: 3

    args = configureArgumentParser()

    # Find Account with products. All instructions must be satisified
    instructions = {
        "AccountType": APIConstants.ACCOUNT_TYPE_INDIVIDUAL,
        "ExpectedSubAccountTypes": [APIConstants.PP_ACCOUNT_TYPE],
        "ExpectedProductTypes": [APIConstants.PP_ACCOUNT_TYPE],
        "IsActive": True,
        "TotalValueGreaterThan": 10,
        "IndividualInvestmentsPresent": True,
        "NumberOfAccountsToFind": 1,

        "InvestmentsToAvoid": ["ModelPortfolioInvestments"],

        # first 5 digits of an WP account, start with 1700x value to allow increaments of 2 i.e 17002xxx, 17004xxx and so on
        "initialAccountNumber": args.initialAccountNumber
    }

    findAccount = FindAccount(args.envName, "test6_wst", "Tester99")
    accounts = findAccount.accountSearchMain(instructions)
    print(f"\n{args.envName} - Found accounts: {accounts}\n")
