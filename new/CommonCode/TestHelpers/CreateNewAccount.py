from CommonCode.TestExecute.Logging import PrintMessage
from TestPages import DataEnums, LongPageEnums, PageEnums
from TestPages.ClientsTabs.SearchResults.AccountSummaryTabPage import AccountSummaryTabPage
from TestPages.PlatformPage import PlatformPage
from TestPages.Wizards.AddNewClientDetailsWizard import AddNewClientDetailsWizard
from TestPages.Wizards.AddNewClientWizard import AddNewClientWizard
from TestPages.Wizards.NewBusinessDocumentsAndDeclarationWizard import NewBusinessDocumentsAndDeclarationWizard
from TestPages.Wizards.NewBusinessReviewWizard import NewBusinessReviewWizard
from TestPages.Wizards.NewBusinessSuccessWizard import NewBusinessSuccessWizard
from TestPages.Wizards.NewClient.ClientTypeTrust.NewBusinessDetailConfirmationWizard import NewBusinessDetailConfirmationWizard
from TestPages.Wizards.NewClient.NewBusinessInvestmentSelectionWizard import NewBusinessInvestmentSelectionWizard
from TestPages.Wizards.NewClient.NewBusinessValidateAndExecuteWizard import NewBusinessValidateAndExecuteWizard
from TestPages.Wizards.NewClient.NewBusinessWizard import NewBusinessWizard
from TestPages.Wizards.NewClient.NewBusinessWrapperDetailsWizard import NewBusinessWrapperDetailsWizard
from TestPages.Wizards.ProductWizards.AdditionalProductDetailsWizard import AdditionalProductDetailsWizard
from TestPages.Wizards.ProductWizards.CashAccountPaymentsInWizard import CashAccountPaymentsInWizard
from TestPages.Wizards.ProductWizards.ISAAdviserChargesWizard import ISAAdviserChargesWizard
from TestPages.Wizards.ProductWizards.ISACompleteDetailsWizard import ISACompleteDetailsWizard
from TestPages.Wizards.ProductWizards.ISAInvestmentSelectionWizard import ISAInvestmentSelectionWizard
from TestPages.Wizards.ProductWizards.ISAPaymentsInWizard import ISAPaymentsInWizard
from TestPages.Wizards.ProductWizards.PersonalPortfolioAdviserChargesWizard import PersonalPortfolioAdviserChargesWizard
from TestPages.Wizards.ProductWizards.PersonalPortfolioCompleteDetailsWizard import PersonalPortfolioCompleteDetailsWizard
from TestPages.Wizards.ProductWizards.PersonalPortfolioInvestmentSelectionWizard import PersonalPortfolioInvestmentSelectionWizard
from TestPages.Wizards.ProductWizards.PersonalPortfolioPaymentsInWizard import PersonalPortfolioPaymentsInWizard
from TestPages.Wizards.Transfers.SIPP.AdviserChargingWizard import AdviserChargingWizard
from TestPages.Wizards.Transfers.SIPP.TaxWrapperAllocationWizard import TaxWrapperAllocationWizard
from TestPages.Wizards.WrapperSelectionWizard import WrapperSelectionWizard


class CreateWrapIndividualOrJointAccount:
    def createNewClientNewBusiness(self, platformPage: PlatformPage, testData):
        PrintMessage("Attempting to create New Client New Business for Account which will be blocked once executed", inStepMessage=True)
        addNewClientWizard = platformPage.navigateToNewClientWizard()
        addNewClientWizard.setWithData(testData[DataEnums.NEW_CLIENT_TYPE])

        PrintMessage("Providing details for New Business Client Details")
        clientDetailsWizard = addNewClientWizard.navigateToAddNewClientDetailsWizard()
        clientDetailsWizard.setWithData(testData[DataEnums.NEW_BUSINESS_CLIENT_DETAILS])

        PrintMessage("Providing details for Full Client Details")
        newBusinessWizard = clientDetailsWizard.selectNextDropdownOption(PageEnums.START_NEW_BUSINESS)
        newBusinessWizard.setWithData(testData[DataEnums.FULL_CLIENT_DETAILS])

        PrintMessage("Providing Wrapper Selection Details")
        wrapperSelectionWizard = newBusinessWizard.navigateToWrapperSelection()
        wrapperSelectionWizard.setWithWrapperData(testData[DataEnums.WRAPPER_SELECTION], testData[DataEnums.PRODUCTS])

        PrintMessage("Providing PP Payment Details")
        ppPaymentWizard: PersonalPortfolioPaymentsInWizard = wrapperSelectionWizard.navigateToNewBusinessPersonalPortfolioPaymentsInWizard()
        ppPaymentWizard.setWithPaymentData(testData[DataEnums.PRODUCTS])

        PrintMessage("Providing details for PP Investment")
        ppInvestmentSelectionWizard: PersonalPortfolioInvestmentSelectionWizard = ppPaymentWizard.navigateToNewPPAdviserChargesWizard(
        ).navigateToNewPPInvestmentSelectionWizard()
        ppInvestmentSelectionWizard.setWithInvestmentData(testData[DataEnums.PRODUCTS])

        PrintMessage("providing details for cash account")
        cashAccPaymentWizard: CashAccountPaymentsInWizard = ppInvestmentSelectionWizard.navigateToPPCompleteDetailsWizard(
        ).navigateToCashAccountPaymentsInWizard()
        cashAccPaymentWizard.setWithPaymentData(testData[DataEnums.PRODUCTS])

        PrintMessage("To navigate back to summary page returning newly created WP account and client name")
        documentsWizard: NewBusinessDocumentsAndDeclarationWizard = cashAccPaymentWizard.navigateToNewBusinessReviewWizard(
        ).navigateToNewBusinessDocumentsAndDeclarationsWizard()
        newBusinessNewClientAccountId = documentsWizard.accountId.text
        newBusinessNewClientName = documentsWizard.clientNameCreatedLabel.text
        documentsWizard.confirmAllCheckBox.click()
        documentsWizard.selectPaperlessOption(testData[DataEnums.WRAPPER_SELECTION][DataEnums.PAPERLESS_PREFERENCE])
        searchSummaryTab: AccountSummaryTabPage = documentsWizard.navigateToNewBusinessSuccessWizard().navigateToClientSummaryPanel()
        PrintMessage("NBNC created successfully and returned the required details")
        return searchSummaryTab, newBusinessNewClientAccountId, newBusinessNewClientName

    def createJointAccount(self, platformPage: PlatformPage, testData, jointCustomerName):
        PrintMessage("# Setup")
        testData[DataEnums.WRAPPER_SELECTION][DataEnums.JOINT_CUSTOMER_NAME] = jointCustomerName

        PrintMessage("Navigate to New client page > Enter Details > Click next and navigate to client details page")
        addNewClientWizard = platformPage.navigateToNewClientWizard()
        addNewClientWizard.setWithData(testData[DataEnums.NEW_CLIENT_TYPE])
        addNewClientDetailsWizard = addNewClientWizard.navigateToAddNewClientDetailsWizard()

        PrintMessage("Client Details page > Select Start New Business from next dropdown > Full Client Details page")
        addNewClientDetailsWizard.setWithData(testData[DataEnums.NEW_CLIENT_DETAILS])
        newBusinessFullClientDetailsWizard = addNewClientDetailsWizard.selectNextDropdownOption(PageEnums.START_NEW_BUSINESS)

        PrintMessage("Full Client Details page > Enter Details > Click Next > Wrapper selection page > Enter Details")
        newBusinessFullClientDetailsWizard.setWithData(testData[DataEnums.FULL_CLIENT_DETAILS])
        newBusinessWrapperSelectionWizard = newBusinessFullClientDetailsWizard.navigateToWrapperSelection()
        newBusinessWrapperSelectionWizard.setWithWrapperData(testData[DataEnums.WRAPPER_SELECTION], testData[DataEnums.PRODUCTS])

        PrintMessage("Navigate to PP payment in page > Enter details")
        newBusinessPPPaymentsInWizard = newBusinessWrapperSelectionWizard.navigateToNewBusinessPersonalPortfolioPaymentsInWizard()
        newBusinessPPPaymentsInWizard.setWithPaymentData(testData[DataEnums.PRODUCTS])

        PrintMessage("Select Transfer in as Yes > Enter all transfer details")
        newBusinessPPPaymentsInWizard.setWithTransferData(testData[DataEnums.PRODUCTS])

        PrintMessage("Navigate to PP Adviser charges page > Enter details")
        newBusinessPPAdviserChargesWizard = newBusinessPPPaymentsInWizard.navigateToNewPPAdviserChargesWizard()
        newBusinessPPAdviserChargesWizard.setWithAdvisorChargesData(testData[DataEnums.PRODUCTS])

        PrintMessage("Navigate to Investment Selection Page > Enter allocations details > Click Next")
        newBusinessPPInvestmentSelectionWizard = newBusinessPPAdviserChargesWizard.navigateToNewPPInvestmentSelectionWizard()
        newBusinessPPInvestmentSelectionWizard.setWithInvestmentData(testData[DataEnums.PRODUCTS])
        newBusinessPPCompleteDetailsWizard = newBusinessPPInvestmentSelectionWizard.navigateToPPCompleteDetailsWizard()

        PrintMessage("Navigate to Cash Account Payments In Page > Provide details for cash account > Navigate to Review Wizard")
        newBusinessCashAccountPaymentsInWizard = newBusinessPPCompleteDetailsWizard.navigateToCashAccountPaymentsInWizard()
        newBusinessCashAccountPaymentsInWizard.setWithPaymentData(testData[DataEnums.PRODUCTS])
        reviewFullClientDetailsWizard = newBusinessCashAccountPaymentsInWizard.navigateToNewBusinessReviewWizard()

        PrintMessage("Navigate to Documents & Declaration Page > Tick the 'Confirm all' checkbox declarations >Then click 'Submit'")
        documentsWizard = reviewFullClientDetailsWizard.navigateToNewBusinessDocumentsAndDeclarationsWizard()
        documentsWizard.confirmAllCheckBox.click()
        documentsWizard.selectPaperlessOption(testData[DataEnums.WRAPPER_SELECTION][DataEnums.PAPERLESS_PREFERENCE])
        newBusinessNewClientAccountId = documentsWizard.accountId.text
        documentsWizard.navigateToNewBusinessSuccessWizard().navigateToClientSummaryPanel()
        PrintMessage("Succesfully created New Business Account With PP Individual and Joint all payments types")
        return newBusinessNewClientAccountId

    def createNewAccountForPPISAOnshoreAndOffshoreBond(self, platformPage: PlatformPage, testData):
        PrintMessage("Navigation > Click on New Client > Enter Client Type details > Click Next: Client Details")
        addNewClientWizard: AddNewClientWizard = platformPage.navigateToNewClientWizard()
        addNewClientWizard.setWithData(testData[DataEnums.NEW_CLIENT_TYPE])
        addNewClientDetailsWizard: AddNewClientDetailsWizard = addNewClientWizard.navigateToAddNewClientDetailsWizard()

        PrintMessage("Client details page > Enter all details > start new business > Proceed to wrapper selection page")
        addNewClientDetailsWizard.setWithData(testData[DataEnums.NEW_CLIENT_DETAILS])
        newBusinessFullClientDetailsWizard: NewBusinessWizard = addNewClientDetailsWizard.selectNextDropdownOption(PageEnums.START_NEW_BUSINESS)
        newBusinessFullClientDetailsWizard.setWithData(testData[DataEnums.FULL_CLIENT_DETAILS])
        newBusinessWrapperSelectionWizard: WrapperSelectionWizard = newBusinessFullClientDetailsWizard.navigateToWrapperSelection()

        PrintMessage(" Wrapper selection page > Enter details > Payments in page")
        newBusinessWrapperSelectionWizard.setWithWrapperData(testData[DataEnums.WRAPPER_SELECTION], testData[DataEnums.PRODUCTS])
        newBusinessISAPaymentsInWizard: ISAPaymentsInWizard = newBusinessWrapperSelectionWizard.navigateNext()

        PrintMessage("ISA Adviser charges page > Enter details > Next > ISA Investment selection page")
        newBusinessISAPaymentsInWizard.setWithPaymentData(testData[DataEnums.PRODUCTS])
        newBusinessISAAdviserChargesWizard: ISAAdviserChargesWizard = newBusinessISAPaymentsInWizard.navigateNext()
        newBusinessISAInvestmentSelectionWizard: ISAInvestmentSelectionWizard = newBusinessISAAdviserChargesWizard.navigateNext()

        PrintMessage("ISA Investment selection page > Enter details > ISA complete details page > PP Payments in page")
        newBusinessISAInvestmentSelectionWizard.setWithInvestmentData(testData[DataEnums.PRODUCTS])
        newBusinessISACompleteDetailsWizard: ISACompleteDetailsWizard = newBusinessISAInvestmentSelectionWizard.navigateNext()
        newBusinessPPPaymentsInWizard: PersonalPortfolioPaymentsInWizard = newBusinessISACompleteDetailsWizard.navigateNext()
        newBusinessPPPaymentsInWizard.setWithPaymentData(testData[DataEnums.PRODUCTS])

        PrintMessage("PP Adviser charges page> Enter details > PP Investment selection page")
        newBusinessPPAdviserChargesWizard: PersonalPortfolioAdviserChargesWizard = newBusinessPPPaymentsInWizard.navigateNext()
        ppInvestmentSelectionWizard: PersonalPortfolioInvestmentSelectionWizard = newBusinessPPAdviserChargesWizard.navigateNext()

        PrintMessage("PP Investment Selection Page > Enter details > PP Complete details page")
        ppInvestmentSelectionWizard.setWithInvestmentData(testData[DataEnums.PRODUCTS])
        newBusinessPPCompleteDetailsWizard: PersonalPortfolioCompleteDetailsWizard = ppInvestmentSelectionWizard.navigateNext()

        PrintMessage("PP Complete details page > Navigations > Additional Product Details > Review details page")
        newBusinessCashAccountPaymentsInWizard: CashAccountPaymentsInWizard = newBusinessPPCompleteDetailsWizard.navigateNext()
        additionalProductDetailsWizard: AdditionalProductDetailsWizard = newBusinessCashAccountPaymentsInWizard.navigateNext()
        additionalProductDetailsWizard.assumedSIPPBondHoldingsCashValueEditField.enterValue(
            testData[DataEnums.ADDITIONAL_PRODUCT_DETAILS][DataEnums.ASSUMED_SIPP_BOND_HOLDINGS])
        reviewFullClientDetailsWizard: NewBusinessReviewWizard = additionalProductDetailsWizard.navigateNext()

        PrintMessage("Documents and declaration page > Confirm all checkbox > Success page")
        documentAndDeclarationWizard: NewBusinessDocumentsAndDeclarationWizard = reviewFullClientDetailsWizard.navigateNext()
        documentAndDeclarationWizard.selectAllDocumentsCheckBox.click(jsClick=True)
        documentAndDeclarationWizard.selectPaperlessOption(testData[DataEnums.WRAPPER_SELECTION][DataEnums.PAPERLESS_PREFERENCE])
        newBusinessSuccessPageToSummaryPage: NewBusinessSuccessWizard = documentAndDeclarationWizard.navigateNext()

        PrintMessage("Success page > Tax wrapper allocation page > enter details > Adviser charging page")
        offShoreBondPage: TaxWrapperAllocationWizard = newBusinessSuccessPageToSummaryPage.navigateNext()
        offShoreBondPage.setWithTaxWrapperAllocationData(testData[DataEnums.PRODUCTS])
        adviserChargingPage: AdviserChargingWizard = offShoreBondPage.navigateNext()

        PrintMessage("Adviser charging page > enter details > next > Investment selection page")
        investmentSelectionPage: NewBusinessInvestmentSelectionWizard = adviserChargingPage.navigateNext()
        investmentSelectionPage.setModelPortfolioDetails(testData.get(DataEnums.BONDS_SELECTION))

        PrintMessage("Investment selection page > enter details > Click next > next > Validate and execute page")
        wrapperDetailsPage: NewBusinessWrapperDetailsWizard = investmentSelectionPage.navigateNext()
        wrapperDetailsPage.setWithData(testData[DataEnums.FULL_CLIENT_DETAILS], testData[DataEnums.PRODUCTS])
        validateAndExecutePage: NewBusinessValidateAndExecuteWizard = wrapperDetailsPage.navigateNext()

        PrintMessage("Navigate > Select the confirmation checkbox > Proceed > Click Complete > Account summary page")
        validateAndExecutePage.waitForDataValidationMessage(LongPageEnums.ALL_DATA_VALIDATED)
        detailsConfirmationPage: NewBusinessDetailConfirmationWizard = validateAndExecutePage.makeOnlyDeclarationAndNavigateToConfirmationPage()
        accountSummaryPage: AccountSummaryTabPage = detailsConfirmationPage.navigateToWrapAccount()
        createdAccountNumber = accountSummaryPage.getHeadAccountFor(PageEnums.CASH_ACCOUNT)
        return accountSummaryPage, createdAccountNumber

    def createNewClientNewBusinessForISA(self, platformPage: PlatformPage, testData):
        PrintMessage("Attempting to create New Client New Business for Account which will be blocked once executed", inStepMessage=True)
        addNewClientWizard: AddNewClientWizard = platformPage.navigateToNewClientWizard()
        addNewClientWizard.setWithData(testData[DataEnums.NEW_CLIENT_TYPE])

        PrintMessage("Providing details for New Business Client Details")
        clientDetailsWizard: AddNewClientDetailsWizard = addNewClientWizard.navigateToAddNewClientDetailsWizard()
        clientDetailsWizard.setWithData(testData[DataEnums.NEW_CLIENT_DETAILS])

        PrintMessage("Providing details for Full Client Details")
        newBusinessWizard: NewBusinessWizard = clientDetailsWizard.selectNextDropdownOption(PageEnums.START_NEW_BUSINESS)
        newBusinessWizard.setWithData(testData[DataEnums.FULL_CLIENT_DETAILS])

        PrintMessage("Providing Wrapper Selection Details")
        wrapperSelectionWizard: WrapperSelectionWizard = newBusinessWizard.navigateToWrapperSelection()
        wrapperSelectionWizard.setWithWrapperData(testData[DataEnums.WRAPPER_SELECTION], testData[DataEnums.PRODUCTS])

        PrintMessage("Providing ISA Payment Details")
        isaPaymentInWizard: ISAPaymentsInWizard = wrapperSelectionWizard.navigateNext()
        isaPaymentInWizard.setWithPaymentData(testData[DataEnums.PRODUCTS])

        PrintMessage("Providing details for ISA Advisor charges")
        isaAdviserChargesWizard: ISAAdviserChargesWizard = isaPaymentInWizard.navigateNext()

        PrintMessage("Providing details for ISA Investment")
        isaInvestmentSelectionWizard: ISAInvestmentSelectionWizard = isaAdviserChargesWizard.navigateNext()
        isaInvestmentSelectionWizard.setWithInvestmentData(testData[DataEnums.PRODUCTS])

        PrintMessage("Providing details for cash account")
        cashAccPaymentWizard: CashAccountPaymentsInWizard = isaInvestmentSelectionWizard.navigateNext(
        ).navigateToCashAccountPaymentsInWizard()

        PrintMessage("Navigate back to summary page returning newly created WP account and client name")
        documentsWizard: NewBusinessDocumentsAndDeclarationWizard = cashAccPaymentWizard.navigateToNewBusinessReviewWizard(
        ).navigateToNewBusinessDocumentsAndDeclarationsWizard()
        newBusinessNewClientAccountId = documentsWizard.accountId.text
        documentsWizard.confirmAllCheckBox.click()
        documentsWizard.selectPaperlessOption(testData[DataEnums.WRAPPER_SELECTION][DataEnums.PAPERLESS_PREFERENCE])
        searchSummaryTab: AccountSummaryTabPage = documentsWizard.navigateToNewBusinessSuccessWizard().navigateToClientSummaryPanel()
        PrintMessage("NBNC created successfully and returned the required details")
        return searchSummaryTab, newBusinessNewClientAccountId
