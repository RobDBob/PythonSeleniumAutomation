from CommonCode.TestExecute.CommandLineArgumentsParser import CommandLineArgumentsParser
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.RunManager import RunManager
from CommonCode.TestExecute.TestContext import Test_Context
from StandAlone.DataInsertionPOC import DataInsertionConsts
from StandAlone.DataInsertionPOC.DataInsertion import DataInsertion
from StandAlone.DataInsertionPOC.ProcessData import AccountDataJSON
from TestData.TestDataLoader import TestDataLoader
from TestPages.Admin.Cash.UnmatchedExpectationsPage import UnmatchedExpectationsPage
from TestPages.ClientsTabs.SearchResults.AccountSummaryTabPage import AccountSummaryTabPage
from TestPages.Enums.ClientTabEnum import ClientTabEnum
from TestPages.Menu import MenuConstants
from TestPages.Wizards.NewBusinessSuccessWizard import NewBusinessSuccessWizard


class NewAccountFactory:
    """
    Reads data from TestData/AccountFiles/{sourceFileName}.yml
    Creates new account based on data
    """

    def __init__(self, environmentName, userName, userPassword):
        self.environmentName = environmentName
        self.userName = userName
        self.userPassword = userPassword

    def createNewAccountFromSourceFile(self, fileName, webdriver=None, documentsToDownload=None):
        """
        Creates new account based on provided instructions in sourceFileName

        if webdriver is not provided, it'll get created and closed within dataInsertion.
        This to prevent unnuecessary creation / closure of webbrowsers i.e. from a test execution level
        """
        dataInsertion = DataInsertion(self.userName, self.userPassword, DataInsertionConsts.LOGIN_TYPE_INTERNAL)
        dataInsertion.NON_SIPP_SUBMIT_APPLICATION_APPLICATION = True
        dataInsertion.DOCUMENTS_AND_DECLARATION_DOWNLOAD_DOCUMENTS = documentsToDownload
        dataInsertion.SHORE_RETURN_LAST_VALIDATION_PAGE = True
        dataInsertion.IGNORE_EXCEPTIONS = False
        dataInsertion.webdriver = webdriver
        accountObj = self.getAccountDataDict(fileName)

        return dataInsertion.runWithData([accountObj]), accountObj

    def createNewAccountAndMatchFunds(self, fileName):
        """
        Creates account
        Activates account
        Matches funds

        Current values are hardcoded as below

        Once account is created and PageObject returned cash is matched
        """
        reconciliationName = "WRAP COLL CLIENT BANK AC - 02288311"
        valueToCashMatch = 24000
        webdriver = None
        PrintMessage(f">>> createNewAccountAndMatchFunds >>> from file: '{fileName}'")
        outComePage, _ = self.createNewAccountFromSourceFile(fileName)

        try:
            assert isinstance(outComePage, NewBusinessSuccessWizard), "Expected NewBusinessSuccessWizard instance"
            webdriver = outComePage.webdriver

            clientSummaryPage: AccountSummaryTabPage = outComePage.navigateToClientSummaryPanel()
            accountNumber = clientSummaryPage.getHeadAccountFor("Cash Account")

            assert isinstance(clientSummaryPage, AccountSummaryTabPage), "Expected AccountSummaryTabPage PageObject"

            rolesTab = clientSummaryPage.navigateToTab(ClientTabEnum.Roles)
            rolesTab.updateAccountStatusToActive()

            mainMenu = rolesTab.navigateToAdminPage().openMainMenu()
            unmatchedExpectationsPage: UnmatchedExpectationsPage = mainMenu.selectMenuItem(MenuConstants.CASH,
                                                                                           MenuConstants.UnmatchedItems,
                                                                                           MenuConstants.UnmatchedExpectations)

            unmatchedExpectationsPage.performCashMatchingProcess(reconciliationName, valueToCashMatch, accountNumber)

        finally:
            if webdriver:
                webdriver.quit()
        PrintMessage(f">>> createNewAccountAndMatchFunds >>> from file: '{fileName}' - DONE")
        return accountNumber

    def getAccountDataDict(self, fileName) -> AccountDataJSON:
        dataLoader = TestDataLoader("AccoundData")
        srcData = dataLoader.getTestDataFromYmlFile(fileName)
        PrintMessage(f"Source data received: len(): {len(srcData)}")
        return AccountDataJSON(srcData["Client"])


if __name__ == '__main__':
    Test_Context.setSetting(ConfigOptions.RUN_HEADLESS, False)
    CommandLineArgumentsParser.processArgumentsEnvironmentSelection(Test_Context)
    # instatianates run manager to ensure folders and etc are created
    RunManager.createFrameworkFolders(Test_Context)
    NewAccountFactory(Test_Context.getSetting(ConfigOptions.ENVIRONMENT), "test50_wst", "Tester99").createNewAccountFromSourceFile("AccountForC1325981.yml")
