import traceback
from retry import retry
from selenium.common.exceptions import TimeoutException
from CommonCode.TestExecute.BrowserSetup import BrowserSetup
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.TestContext import Test_Context
from CommonCode.TestHelpers.BrowserHelper import BrowserHelper
from StandAlone.DataInsertionPOC import DataInsertionConsts
from StandAlone.DataInsertionPOC.ProcessData import AccountDataJSON
from TestPages import DataEnums, PageEnums
from TestPages.LoginPages.WrapProdLoginPage import WrapProdLoginPage
from TestPages.PlatformLoginPage import PlatformLoginPage
from TestPages.PlatformPage import PlatformPage
from TestPages.Wizards.AddNewClientDetailsWizard import AddNewClientDetailsWizard
from TestPages.Wizards.AddNewClientWizard import AddNewClientWizard
from TestPages.Wizards.NewBusinessDocumentsAndDeclarationWizard import NewBusinessDocumentsAndDeclarationWizard
from TestPages.Wizards.NewBusinessReviewWizard import NewBusinessReviewWizard
from TestPages.Wizards.NewBusinessSuccessWizard import NewBusinessSuccessWizard
from TestPages.Wizards.NewClient.NewBusinessInvestmentSelectionWizard import NewBusinessInvestmentSelectionWizard
from TestPages.Wizards.NewClient.NewBusinessValidateAndExecuteWizard import NewBusinessValidateAndExecuteWizard
from TestPages.Wizards.NewClient.NewBusinessWizard import NewBusinessWizard
from TestPages.Wizards.NewClient.NewBusinessWrapperDetailsWizard import NewBusinessWrapperDetailsWizard
from TestPages.Wizards.ProductWizards.AbrdnSIPPAdviserChargesWizard import AbrdnSIPPAdviserChargesWizard
from TestPages.Wizards.ProductWizards.AbrdnSIPPCompleteDetailsWizard import AbrdnSIPPCompleteDetailsWizard
from TestPages.Wizards.ProductWizards.AbrdnSippInvestmentSelectionWizard import AbrdnSippInvestmentSelectionWizard
from TestPages.Wizards.ProductWizards.AbrdnSIPPPaymentsInWizard import AbrdnSIPPPaymentsInWizard
from TestPages.Wizards.ProductWizards.AdditionalProductDetailsWizard import AdditionalProductDetailsWizard
from TestPages.Wizards.ProductWizards.CashAccountPaymentsInWizard import CashAccountPaymentsInWizard
from TestPages.Wizards.ProductWizards.ISAAdviserChargesWizard import ISAAdviserChargesWizard
from TestPages.Wizards.ProductWizards.ISACompleteDetailsWizard import ISACompleteDetailsWizard
from TestPages.Wizards.ProductWizards.ISAInvestmentSelectionWizard import ISAInvestmentSelectionWizard
from TestPages.Wizards.ProductWizards.ISAPaymentsInWizard import ISAPaymentsInWizard
from TestPages.Wizards.ProductWizards.ISAWithdrawalsWizard import ISAWithdrawalsWizard
from TestPages.Wizards.ProductWizards.PersonalPortfolioAdviserChargesWizard import PersonalPortfolioAdviserChargesWizard
from TestPages.Wizards.ProductWizards.PersonalPortfolioCompleteDetailsWizard import PersonalPortfolioCompleteDetailsWizard
from TestPages.Wizards.ProductWizards.PersonalPortfolioInvestmentSelectionWizard import PersonalPortfolioInvestmentSelectionWizard
from TestPages.Wizards.ProductWizards.PersonalPortfolioPaymentsInWizard import PersonalPortfolioPaymentsInWizard
from TestPages.Wizards.ProductWizards.PersonalPortfolioWithdrawalsWizard import PersonalPortfolioWithdrawalsWizard
from TestPages.Wizards.ProductWizards.ProductWizardBase import ProductWizardBase
from TestPages.Wizards.Transfers.SIPP.AdviserChargingWizard import AdviserChargingWizard
from TestPages.Wizards.Transfers.SIPP.TaxWrapperAllocationWizard import TaxWrapperAllocationWizard
from TestPages.Wizards.WrapperSelectionWizard import WrapperSelectionWizard


# pylint: disable = broad-exception-caught
class DataInsertion:
    # instructions used by non-client onboarding actions, i.e. e2e tests
    NON_SIPP_SUBMIT_APPLICATION_APPLICATION = False
    DOCUMENTS_AND_DECLARATION_DOWNLOAD_DOCUMENTS = None
    SHORE_RETURN_LAST_VALIDATION_PAGE = False

    IGNORE_EXCEPTIONS = True

    currentClientsAccountNumber = None
    currentClientsName = None

    loginName = None
    loginPassword = None
    loginType = None

    _webdriver = None

    def __init__(self, loginName, loginPassword, loginType):
        self.loginName = loginName
        self.loginPassword = loginPassword
        self.loginType = loginType

    def _innerUseLogin(self, webdriver):
        loginPage = PlatformLoginPage(webdriver)
        loginPage.performLogin(userName=self.loginName, password=self.loginPassword)
        return PlatformPage(webdriver)

    def _unipassLoginWrap(self, webdriver):
        unipassLogin = WrapProdLoginPage(webdriver).navigateToUnipassLogin()
        return unipassLogin.performLogin(self.loginName, self.loginPassword)

    def performLogin(self, webdriver):
        if self.loginType == DataInsertionConsts.LOGIN_TYPE_INTERNAL:
            PrintMessage("Perform login > LOGIN_TYPE_INNER", inStepMessage=True)
            return self._innerUseLogin(webdriver)
        if self.loginType == DataInsertionConsts.LOGIN_TYPE_UNIPASS:
            PrintMessage("Perform login > LOGIN_TYPE_UNIPASS", inStepMessage=True)
            return self._unipassLoginWrap(webdriver)
        return None

    @retry(exceptions=TimeoutException, tries=2)
    def getSession(self, platformPage: PlatformPage):
        if platformPage is None or platformPage.webdriver is None:
            return self.performLogin(self.webdriver)

        return platformPage

    def noteCurrentAccountDetails(self, wizardPage: ProductWizardBase):
        if self.currentClientsAccountNumber:
            return

        self.currentClientsAccountNumber = wizardPage.currentAccountNumber
        self.currentClientsName = wizardPage.currentUserName

    def addNewClientBusiness(self, addNewClientPage: AddNewClientWizard, accountData: AccountDataJSON):
        # CodeNote: using currentTestId variable to carry stage name for evidence screenshots
        addNewClientPage.testContext.clientOnboardingEvidenceFolderName = accountData._getClientEvidenceFolderName()

        self.currentClientsAccountNumber = None
        self.currentClientsName = None
        addNewClientPage.setWithData(accountData._getClientType())

        addNewClientDetails: AddNewClientDetailsWizard = addNewClientPage.navigateToAddNewClientDetailsWizard()
        addNewClientDetails.setWithData(accountData._getClientDetails())

        newBusiness: NewBusinessWizard = addNewClientDetails.selectNextDropdownOption(PageEnums.START_NEW_BUSINESS)
        newBusiness.setWithData(accountData._getClientDetails())

        wrapperSelection: WrapperSelectionWizard = newBusiness.navigateToWrapperSelection()

        wrapperData = accountData.wrapperData
        wrapperSelection.setWithWrapperData(wrapperData, accountData.productsData)
        wizardPage = wrapperSelection.navigateNext()

        while True:
            self.noteCurrentAccountDetails(wizardPage)

            if isinstance(wizardPage, AbrdnSIPPPaymentsInWizard):
                wizardPage.setWithPaymentData(accountData.productsData, bankData=accountData.bankData)
                wizardPage.setWithTransferData(accountData.productsData)

            elif isinstance(wizardPage, AbrdnSIPPAdviserChargesWizard):
                wizardPage.setWithAdvisorChargesData(accountData.productsData)

            elif isinstance(wizardPage, AbrdnSippInvestmentSelectionWizard):
                wizardPage.setWithInvestmentData(accountData.productsData)

            elif isinstance(wizardPage, AbrdnSIPPCompleteDetailsWizard):
                pass

            elif isinstance(wizardPage, ISAPaymentsInWizard):
                wizardPage.setWithPaymentData(accountData.productsData, bankData=accountData.bankData)
                wizardPage.setWithTransferData(accountData.productsData)

            elif isinstance(wizardPage, ISAAdviserChargesWizard):
                wizardPage.setWithAdvisorChargesData(accountData.productsData)

            elif isinstance(wizardPage, ISAInvestmentSelectionWizard):
                wizardPage.setWithInvestmentData(accountData.productsData)

            elif isinstance(wizardPage, ISACompleteDetailsWizard):  # end of ISA journey, onto next
                pass

            elif isinstance(wizardPage, NewBusinessReviewWizard):  # possibly last page - next page avialable is Documents & declarations
                pass

            elif isinstance(wizardPage, ISAWithdrawalsWizard):
                PrintMessage(" >>> Withdrawals not implemented <<< ", inStepMessage=True)

            elif isinstance(wizardPage, NewBusinessDocumentsAndDeclarationWizard):
                wizardPage.skipBankPromptForUnverifiedDetails()

                if self.DOCUMENTS_AND_DECLARATION_DOWNLOAD_DOCUMENTS:
                    wizardPage.documentDownloader.cleanDownloadFolder()
                    wizardPage.downloadDocuments(self.DOCUMENTS_AND_DECLARATION_DOWNLOAD_DOCUMENTS)

                wizardPage.selectPaperlessOption(PageEnums.YES)
                wizardPage.confirmAllIfRequired()

                # without BONDS, next button text be Submit
                if wizardPage.nextButton.text == PageEnums.SUBMIT:
                    # this is used in e2e tests
                    if self.NON_SIPP_SUBMIT_APPLICATION_APPLICATION:
                        PrintMessage("Submitting application - used only in non-client onboarding processes", inStepMessage=True)
                        return wizardPage.navigateToNewBusinessSuccessWizard()

                    return wizardPage.saveAndExit()

            elif isinstance(wizardPage, PersonalPortfolioPaymentsInWizard):
                wizardPage.setWithPaymentData(accountData.productsData, bankData=accountData.bankData)
                wizardPage.setWithTransferData(accountData.productsData)

            elif isinstance(wizardPage, PersonalPortfolioAdviserChargesWizard):
                wizardPage.setWithAdvisorChargesData(accountData.productsData)

            elif isinstance(wizardPage, PersonalPortfolioInvestmentSelectionWizard):
                wizardPage.setWithInvestmentData(accountData.productsData)

            elif isinstance(wizardPage, PersonalPortfolioWithdrawalsWizard):
                # No withdrawals - skip
                pass

            elif isinstance(wizardPage, PersonalPortfolioCompleteDetailsWizard):
                pass

            elif isinstance(wizardPage, CashAccountPaymentsInWizard):
                wizardPage.setWithPaymentData(accountData.productsData)

            elif isinstance(wizardPage, AdditionalProductDetailsWizard):
                shoreProductData = accountData.getProductData(DataEnums.PRODUCT_ABRDN_SIPP)
                wizardPage.setWithProductDetailsData(shoreProductData, accountData.bankData)

            elif isinstance(wizardPage, NewBusinessSuccessWizard):
                # next action is triggered via navigateNext, possibly onto SIPP journey
                pass

            elif isinstance(wizardPage, TaxWrapperAllocationWizard):
                # skip Notify when funds received, not required: Lisa Turley
                wizardPage.setWithTaxWrapperAllocationData(accountData.productsData)

            elif isinstance(wizardPage, AdviserChargingWizard):
                # skip Notify when funds received, not required: Lisa Turley
                wizardPage.setWithAdvisorChargesData(accountData.productsData)

            elif isinstance(wizardPage, NewBusinessInvestmentSelectionWizard):
                wizardPage.setWithData(accountData.getProductData(DataEnums.PRODUCT_OFFSHORE_BOND).get(DataEnums.INVESTMENTS))
                wizardPage.setWithData(accountData.getProductData(DataEnums.PRODUCT_ONSHORE_BOND).get(DataEnums.INVESTMENTS))

                wizardPage.browserHelper.makeTestEvidenceScreenshot("BONDS_InvestmentAllocationWizard")

            elif isinstance(wizardPage, NewBusinessWrapperDetailsWizard):
                wizardPage.setWithData(accountData.clientsData, accountData.productsData)

                wizardPage.browserHelper.makeTestEvidenceScreenshot("BONDS_WrapperDetails")

            elif isinstance(wizardPage, NewBusinessValidateAndExecuteWizard):
                PrintMessage(f"Bonds - last page '{self.currentClientsName}': '{self.currentClientsAccountNumber}'", inStepMessage=True)
                wizardPage.browserHelper.makeTestEvidenceScreenshot("BONDS_NewBusinessValidateAndExecuteWizard")
                if self.SHORE_RETURN_LAST_VALIDATION_PAGE:
                    return wizardPage
                return wizardPage.saveAndExit()

            else:
                PrintMessage(
                    f"Unknown page, previously on: '{type(wizardPage)}' exiting - '{self.currentClientsName}': '{self.currentClientsAccountNumber}'",
                    inStepMessage=True)
                break

            wizardPage = wizardPage.navigateNext()

        return False

    def runWithData(self, srcClientData: list):
        goodAccounts = []
        badAccounts = []
        platformPage = None
        try:
            for clientData in srcClientData:
                outcome = None
                platformPage = self.getSession(platformPage)

                try:
                    addNewClientPage: AddNewClientWizard = platformPage.navigateToNewClientWizard()
                    outcome = self.addNewClientBusiness(addNewClientPage, clientData)

                except Exception as e:
                    tb = traceback.format_exc()
                    PrintMessage(f">>>>>>>>>>>>>>>>>>>>>> Encountered exception {type(e)}, with args {e.args}")
                    PrintMessage(str(e))
                    PrintMessage(f"traceback: {tb}")

                    clientDetail = f"User: {self.currentClientsName} with Account Number: {self.currentClientsAccountNumber}"
                    PrintMessage(f">>>>>>> Encountered exception >>>>>>> Cancelling OUT! '{clientDetail}'", inStepMessage=True)

                    if not self.IGNORE_EXCEPTIONS:
                        # pylint: disable = broad-exception-raised
                        raise Exception(str(e)) from e

                    if platformPage and platformPage.webdriver:
                        screenshoPath = BrowserHelper(platformPage.webdriver, Test_Context).makeScreenshot("runWithData-error-inner-loop")

                        badAccounts.append({"accountNumber": self.currentClientsAccountNumber,
                                           "currentUserName": self.currentClientsName, "screenshot": screenshoPath})

                        self.webdriver.quit()
                        self.webdriver = None
                        platformPage = None

                finally:
                    if outcome:
                        message = f">> ACCOUNT: {self.currentClientsAccountNumber} for CLIENT: {self.currentClientsName} created!!"
                        PrintMessage(f"----==== SUCCESS {message}", inStepMessage=True)
                        goodAccounts.append({"accountNumber": self.currentClientsAccountNumber, "currentUserName": self.currentClientsName})

        except Exception:
            if platformPage and platformPage.webdriver:
                screenshoPath = BrowserHelper(platformPage.webdriver, Test_Context).makeScreenshot("runWithData-error-outer-loop")
            raise

        finally:
            PrintMessage("------------------ GOOD RESULTS")
            for result in goodAccounts:
                PrintMessage(result, inStepMessage=True)
            PrintMessage("------------------ BAD RESULTS")
            for result in badAccounts:
                PrintMessage(result)

        return outcome

    @property
    def webdriver(self):
        if not self._webdriver:
            self._webdriver = BrowserSetup(Test_Context).setup()
        return self._webdriver

    @webdriver.setter
    def webdriver(self, value):
        self._webdriver = value
