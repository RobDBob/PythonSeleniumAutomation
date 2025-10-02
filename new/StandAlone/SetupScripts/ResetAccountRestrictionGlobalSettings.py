from retry import retry
from selenium.common.exceptions import TimeoutException
from CommonCode.TestExecute.BrowserSetup import BrowserSetup
from CommonCode.TestExecute.CommandLineArgumentsParser import CommandLineArgumentsParser
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.TestContext import Test_Context
from TestPages import PageEnums
from TestPages.Admin.AccountRestrictions.SuspendedActivityConfigurationPage import SuspendedActivityConfigurationPage
from TestPages.Menu import MenuConstants
from TestPages.PlatformLoginPage import PlatformLoginPage


@retry(exceptions=TimeoutException, delay=30, tries=5)
def logAsUser(userNumber):
    Test_Context.setSetting(ConfigOptions.RUN_HEADLESS, True)
    webdriver = BrowserSetup(Test_Context).setup()
    return PlatformLoginPage(webdriver).logAsUser(userNumber)


def resetCheckboxForRestrictions(suspendedActivityConfigPage: SuspendedActivityConfigurationPage, reasonForSuspending, skipResetFlag=False):
    """
    Method to uncheck all available restriction checkboxes if they are already ticked for respective reason for suspending
    """

    suspendedActivityConfigPage.reasonForSuspendingDropdown.selectOption(reasonForSuspending)
    suspendedActivityConfigPage.editButton.waitForElement()
    suspendedActivityConfigPage.editButton.click(jsClick=True)

    if suspendedActivityConfigPage.getFeeAndChargesSelectedRow(PageEnums.FEE_POSTING).suspendedCheckBox.isChecked:
        suspendedActivityConfigPage.feesAndChargesTable.waitForElement()
        suspendedActivityConfigPage.getFeeAndChargesSelectedRow(PageEnums.FEE_POSTING).suspendedCheckBox.jsClick()

    if suspendedActivityConfigPage.getPaymentsSelectedRow(PageEnums.WITHDRAWALS).suspendedActivityCheckBox.isChecked:
        suspendedActivityConfigPage.paymentsTable.waitForElement()
        suspendedActivityConfigPage.getPaymentsSelectedRow(PageEnums.WITHDRAWALS).suspendedActivityCheckBox.jsClick()

    if suspendedActivityConfigPage.getPaymentsSelectedRow(PageEnums.DEPOSITS).suspendedActivityCheckBox.isChecked:
        suspendedActivityConfigPage.paymentsTable.waitForElement()
        suspendedActivityConfigPage.getPaymentsSelectedRow(PageEnums.DEPOSITS).suspendedActivityCheckBox.jsClick()

    if not skipResetFlag:

        if suspendedActivityConfigPage.getPaymentsSelectedRow(PageEnums.WITHDRAWALS).flagForApprovalCheckBox.isChecked:
            suspendedActivityConfigPage.paymentsTable.waitForElement()
            suspendedActivityConfigPage.getPaymentsSelectedRow(PageEnums.WITHDRAWALS).flagForApprovalCheckBox.jsClick()

        if suspendedActivityConfigPage.getPaymentsSelectedRow(PageEnums.DEPOSITS).flagForApprovalCheckBox.isChecked:
            suspendedActivityConfigPage.paymentsTable.waitForElement()
            suspendedActivityConfigPage.getPaymentsSelectedRow(PageEnums.DEPOSITS).flagForApprovalCheckBox.jsClick()

    if suspendedActivityConfigPage.getTransactionalSelectedRow(PageEnums.BUYS).suspendedCheckBox.isChecked:
        suspendedActivityConfigPage.paymentsTable.waitForElement()
        suspendedActivityConfigPage.getTransactionalSelectedRow(PageEnums.BUYS).suspendedCheckBox.jsClick()

    if suspendedActivityConfigPage.getTransactionalSelectedRow(PageEnums.SELLS).suspendedCheckBox.isChecked:
        suspendedActivityConfigPage.paymentsTable.waitForElement()
        suspendedActivityConfigPage.getTransactionalSelectedRow(PageEnums.SELLS).suspendedCheckBox.jsClick()

    if suspendedActivityConfigPage.getTransactionalSelectedRow(PageEnums.TRANSFERS_OUT).suspendedCheckBox.isChecked:
        suspendedActivityConfigPage.paymentsTable.waitForElement()
        suspendedActivityConfigPage.getTransactionalSelectedRow(PageEnums.TRANSFERS_OUT).suspendedCheckBox.jsClick()

    if suspendedActivityConfigPage.getTransactionalSelectedRow(PageEnums.INTER_ACCOUNT_TRANSFER).suspendedCheckBox.isChecked:
        suspendedActivityConfigPage.paymentsTable.waitForElement()
        suspendedActivityConfigPage.getTransactionalSelectedRow(PageEnums.INTER_ACCOUNT_TRANSFER).suspendedCheckBox.jsClick()

    suspendedActivityConfigPage.saveButton.click()


def rejectAllRequests(firstTestUserNumber):
    PrintMessage("# Step - 1 : Login to Platform as First Test User")
    platformPage = logAsUser(userNumber=firstTestUserNumber)
    webdriver = platformPage.webdriver
    try:
        PrintMessage("# Step - 2 : Navigate to Suspended Reason Authorisation Page and Reject any existing requests unprocessed")
        suspendedReasonAuthorisationPage = platformPage.navigateToAdminPage().openMainMenu().selectMenuItem(
            MenuConstants.AccountRestrictions, MenuConstants.SuspendedReasonAuthorisation)
        suspendedReasonAuthorisationPage.rejectAllRequests()

        PrintMessage("# Step - 3 : Logout and Login to Platform as Second Test User")
        profileSettingPage = suspendedReasonAuthorisationPage.navigateToProfileSetting()
        profileSettingPage.logOutButton.click()
    finally:
        if webdriver:
            webdriver.quit()


def resetRestrictions(secondTestUserNumber):
    platformPage = logAsUser(userNumber=secondTestUserNumber)
    webdriver = platformPage.webdriver

    try:
        PrintMessage("# Step - 4 : Navigate to Suspended Activity Config Page")
        suspendedActivityConfigPage = platformPage.navigateToAdminPage().openMainMenu().selectMenuItem(
            MenuConstants.AccountRestrictions, MenuConstants.SuspendedActivityConfiguration)

        PrintMessage("# Step - 5 : Method resetCheckboxForRestrictions is called for each restrictions to be reset")
        resetCheckboxForRestrictions(suspendedActivityConfigPage, PageEnums.ADDITIONAL_CLIENT_SECURITY_REQUIRED)
        resetCheckboxForRestrictions(suspendedActivityConfigPage, PageEnums.AML_SAR)
        resetCheckboxForRestrictions(suspendedActivityConfigPage, PageEnums.AUTHORITY_REQUEST_POLICE_COURTS)
        resetCheckboxForRestrictions(suspendedActivityConfigPage, PageEnums.BANKRUPTCY_INDIVIDUAL)
        resetCheckboxForRestrictions(suspendedActivityConfigPage, PageEnums.BANKRUPTCY_JOINT)
        resetCheckboxForRestrictions(suspendedActivityConfigPage, PageEnums.FRAUDULENT_ACCOUNT)
        resetCheckboxForRestrictions(suspendedActivityConfigPage, PageEnums.GONE_AWAY_EARLY)
        resetCheckboxForRestrictions(suspendedActivityConfigPage, PageEnums.GONE_AWAY_NO_CONTACT)
        resetCheckboxForRestrictions(suspendedActivityConfigPage, PageEnums.HIGH_RISK_CUSTOMER, skipResetFlag=True)
        resetCheckboxForRestrictions(suspendedActivityConfigPage, PageEnums.LEGAL_COURT_ORDER_FROZEN)
        resetCheckboxForRestrictions(suspendedActivityConfigPage, PageEnums.PENSION_SHARING_ORDER)
        resetCheckboxForRestrictions(suspendedActivityConfigPage, PageEnums.PEP, skipResetFlag=True)
        resetCheckboxForRestrictions(suspendedActivityConfigPage, PageEnums.SUBJECT_TO_SANCTIONS, skipResetFlag=True)
        resetCheckboxForRestrictions(suspendedActivityConfigPage, PageEnums.SUSPECTED_FRAUD)

        PrintMessage("# Step - 6 : Logout and Login to Platform as Third Test User")
        profileSettingPage = suspendedActivityConfigPage.navigateToProfileSetting()
        profileSettingPage.logOutButton.click()
    finally:
        if webdriver:
            webdriver.quit()


def authoriseAllRequests(thirdTestUserNumber):
    platformPage = logAsUser(userNumber=thirdTestUserNumber)
    webdriver = platformPage.webdriver
    try:
        PrintMessage("# Step - 7 : Navigate to Suspended Reason Authorisation Page and Authorise all existing requests")
        suspendedReasonAuthorisationPage = platformPage.navigateToAdminPage().openMainMenu().selectMenuItem(
            MenuConstants.AccountRestrictions, MenuConstants.SuspendedReasonAuthorisation)
        suspendedReasonAuthorisationPage.authoriseAllRequests()
    finally:
        if webdriver:
            webdriver.quit()


def resetAccountRestrictionGlobalSettings(environment):
    """
    This script will uncheck all selected Account Restrictions and Authorise the changes so that there wont be any active restrictions globally set.
    """
    PrintMessage("# Setup : Users required for operation are allocated here")
    firstTestUserNumber = 157
    secondTestUserNumber = 158
    thirdTestUserNumber = 159

    rejectAllRequests(firstTestUserNumber)
    resetRestrictions(secondTestUserNumber)
    authoriseAllRequests(thirdTestUserNumber)
    PrintMessage(f"Account Restrictions Global Settings reset for - {environment}")


if __name__ == '__main__':
    CommandLineArgumentsParser.processArgumentsEnvironmentSelection(Test_Context)
    resetAccountRestrictionGlobalSettings(Test_Context.getSetting(ConfigOptions.ENVIRONMENT))
