from retry import retry
from selenium.webdriver.common.by import By
from CommonCode.CustomExceptions import UIException
from CommonCode.TestExecute.Logging import PrintMessage
from TestPages import PageEnums
from TestPages.ClientsTabs.SearchResults.SinglePaymentWarningMessagePage import SinglePaymentWarningMessagePage
from TestPages.NoChangeTool.NoChangeToolPage import NoChangeToolPage
from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject
from TestPages.PageObjects.BaseObjects.Button import Button
from TestPages.ProductWizards.ABERDEENJSIPPSellOrderSetupPage import ABERDEENJSIPPSellOrderSetupPage
from TestPages.ProductWizards.ABERDEENSIPPSellOrderSetupPage import ABERDEENSIPPSellOrderSetupPage
from TestPages.ProductWizards.ABERDEENSIPPSwitchOrderSetupPage import ABERDEENSIPPSwitchOrderSetupPage
from TestPages.ProductWizards.ABRDNJSIPPBuyOrderSetupPage import ABRDNJSIPPBuyOrderSetupPage
from TestPages.ProductWizards.ABRDNSIPPBuyOrderSetupPage import ABRDNSIPPBuyOrderSetupPage
from TestPages.ProductWizards.CashAccountSinglePaymentBase import CashAccountSinglePaymentBase
from TestPages.ProductWizards.ISABuyOrderSetupPage import ISABuyOrderSetupPage
from TestPages.ProductWizards.ISACurrentClientRegularPaymentInstructionsPage import ISACurrentClientRegularPaymentInstructionsPage
from TestPages.ProductWizards.ISAEditRegularPaymentInPage import ISAEditRegularPaymentInPage
from TestPages.ProductWizards.ISASellOrderSetupPage import ISASellOrderSetupPage
from TestPages.ProductWizards.ISAStocksAndSharesRegularPaymentInPage import ISAStocksAndSharesRegularPaymentInPage
from TestPages.ProductWizards.ISAStocksAndSharesSinglePaymentBase import ISAStocksAndSharesSinglePaymentBase
from TestPages.ProductWizards.ISASwitchOrderSetupPage import ISASwitchOrderSetupPage
from TestPages.ProductWizards.PersonalPortfolioRegularPaymentInPage import PersonalPortfolioRegularPaymentInPage
from TestPages.ProductWizards.PersonalPortfolioSinglePaymentBase import PersonalPortfolioSinglePaymentBase
from TestPages.ProductWizards.PersonalPortfolioToSharesAndStocksISA import PersonalPortfolioToSharesAndStocksISA
from TestPages.ProductWizards.PortfolioInvestments.PPBuyOrderSetupPage import PPBuyOrderSetupPage
from TestPages.ProductWizards.PPEditRegularPaymentInPage import PPEditRegularPaymentInPage
from TestPages.ProductWizards.SIPPDealPlaceOrderSetupPage import SIPPDealPlaceOrderSetupPage
from TestPages.ProductWizards.WhatIfToolPage import WhatIfToolPage
from TestPages.WebDriver.ObjProduction import manufacture
from TestPages.Withdrawals.CreateOrdersWithdrawalsPage import CreateOrdersWithdrawalsPage
from TestPages.Wizards.ProductWizards.AbrdnSIPPCancelTailoredDrawdownReviewPage import AbrdnSIPPCancelTailoredDrawdownReviewPage
from TestPages.Wizards.ProductWizards.AbrdnSIPPEditIncomeDrawdownDetailsWizard import AbrdnSIPPEditIncomeDrawdownDetailsWizard
from TestPages.Wizards.ProductWizards.AbrdnSIPPGadReviewIncomePaymentDetailsPage import AbrdnSIPPGadReviewIncomePaymentDetailsPage
from TestPages.Wizards.ProductWizards.AbrdnSIPPOneOffPaymentIncomePaymentDetails import AbrdnSIPPOneOffPaymentIncomePaymentDetails
from TestPages.Wizards.ProductWizards.AbrdnSIPPPaymentsInWizard import AbrdnSIPPPaymentsInWizard
from TestPages.Wizards.ProductWizards.AbrdnSIPPSelectArrangementsToConvertPage import AbrdnSIPPSelectArrangementsToConvertPage
from TestPages.Wizards.ProductWizards.AbrdnSIPPTakePensionBenefitPensionBenefitsDetails import AbrdnSIPPTakePensionBenefitPensionBenefitsDetails
from TestPages.Wizards.ProductWizards.AbrdnSIPPTopupWithImmediateTFLSPaymentsInWizard import AbrdnSIPPTopupWithImmediateTFLSPaymentsInWizard
from TestPages.Wizards.Transfers.SIPP.PensionTransfersToWrapWizard import PensionTransfersToWrapWizard


class DropearListPanel(BaseTestObject):
    """
    Class used in search summary
    """

    def __init__(self, webdriver, parentElement, locator, productName):
        super().__init__(webdriver, parentElement, *locator)
        self.productName = productName

    # pylint: disable=R0911
    def getPage(self, optionName):
        match self.productName:
            case PageEnums.PRODUCT_ISA_STOCKS_AND_SHARES:
                match optionName:
                    case PageEnums.SINGLE_PAYMENT:
                        return ISAStocksAndSharesSinglePaymentBase(self.webdriver)
                    case PageEnums.ADD_REGULAR_PAYMENT:
                        return ISAStocksAndSharesRegularPaymentInPage(self.webdriver)
                    case PageEnums.EDIT_REGULAR_PAYMENT:
                        return ISAEditRegularPaymentInPage(self.webdriver)
                    case PageEnums.LaunchWhatIfTool:
                        return WhatIfToolPage(self.webdriver)
                    case PageEnums.LaunchNoChangeTool:
                        return NoChangeToolPage(self.webdriver)
                    case PageEnums.BUY:
                        return ISABuyOrderSetupPage(self.webdriver)
                    case PageEnums.SELL:
                        return ISASellOrderSetupPage(self.webdriver)
                    case PageEnums.Switch:
                        return ISASwitchOrderSetupPage(self.webdriver)
                    case PageEnums.WITHDRAW:
                        return CreateOrdersWithdrawalsPage(self.webdriver)
                    case PageEnums.THIRD_PARTY_EDIT_REGULAR_PAYMENT:
                        return ISACurrentClientRegularPaymentInstructionsPage(self.webdriver)
                    case _:
                        return SinglePaymentWarningMessagePage(self.webdriver)

            case PageEnums.PRODUCT_PERSONAL_PORTFOLIO:
                match optionName:
                    case PageEnums.SINGLE_PAYMENT:
                        return PersonalPortfolioSinglePaymentBase(self.webdriver)
                    case PageEnums.ADD_REGULAR_PAYMENT:
                        return PersonalPortfolioRegularPaymentInPage(self.webdriver)
                    case PageEnums.EDIT_REGULAR_PAYMENT:
                        return PPEditRegularPaymentInPage(self.webdriver)
                    case PageEnums.LaunchNoChangeTool:
                        return NoChangeToolPage(self.webdriver)
                    case PageEnums.BUY:
                        return PPBuyOrderSetupPage(self.webdriver)
                    case PageEnums.PP_TO_S_AND_S_ISA:
                        return PersonalPortfolioToSharesAndStocksISA(self.webdriver)
                    case _:
                        return SinglePaymentWarningMessagePage(self.webdriver)
            case PageEnums.CASH_ACCOUNT:
                match optionName:
                    case PageEnums.SINGLE_PAYMENT:
                        return CashAccountSinglePaymentBase(self.webdriver)
                    case PageEnums.ADD_REGULAR_PAYMENT:
                        from TestPages.ProductWizards.CashAccountRegularPaymentInBasePage import CashAccountRegularPaymentInBasePage
                        return CashAccountRegularPaymentInBasePage(self.webdriver)
                    case PageEnums.WITHDRAW:
                        return CreateOrdersWithdrawalsPage(self.webdriver)
                    case PageEnums.EDIT_REGULAR_PAYMENT:
                        from TestPages.ProductWizards.CashAccountRegularPaymentInBasePage import CashAccountRegularPaymentInBasePage
                        return CashAccountRegularPaymentInBasePage(self.webdriver)
            case PageEnums.SIPP:
                match optionName:
                    case PageEnums.SINGLE_PAYMENT:
                        return PensionTransfersToWrapWizard(self.webdriver)
                    case PageEnums.BUY:
                        return SIPPDealPlaceOrderSetupPage(self.webdriver)
            case PageEnums.ABRDN_SIPP | PageEnums.ABERDEEN_SIPP:
                match optionName:
                    case PageEnums.BUY:
                        return ABRDNSIPPBuyOrderSetupPage(self.webdriver)
                    case PageEnums.SELL:
                        return ABERDEENSIPPSellOrderSetupPage(self.webdriver)
                    case PageEnums.Switch:
                        return ABERDEENSIPPSwitchOrderSetupPage(self.webdriver)
                    case PageEnums.ADD_REGULAR_PAYMENT:
                        return AbrdnSIPPPaymentsInWizard(self.webdriver)
                    case PageEnums.EDIT_REGULAR_PAYMENT:
                        return AbrdnSIPPPaymentsInWizard(self.webdriver)
                    case PageEnums.SINGLE_PAYMENT:
                        return AbrdnSIPPPaymentsInWizard(self.webdriver)
                    case PageEnums.ONE_OFF_INCOME_PAYMENT:
                        return AbrdnSIPPOneOffPaymentIncomePaymentDetails(self.webdriver)
                    case PageEnums.CONVERT_CAPPED_TO_FLEXIBLE_DRAWDOWN:
                        return AbrdnSIPPSelectArrangementsToConvertPage(self.webdriver)
                    case PageEnums.TAKE_PENSION_BENEFITS:
                        return AbrdnSIPPTakePensionBenefitPensionBenefitsDetails(self.webdriver)
                    case PageEnums.TOP_UP_WITH_IMMEDIATE_TAXFREE_LUMP_SUM:
                        return AbrdnSIPPTopupWithImmediateTFLSPaymentsInWizard(self.webdriver)
                    case PageEnums.GAD_REVIEW:
                        return AbrdnSIPPGadReviewIncomePaymentDetailsPage(self.webdriver)
                    case PageEnums.CANCEL_TAILORED_DRAWDOWN:
                        return AbrdnSIPPCancelTailoredDrawdownReviewPage(self.webdriver)
                    case PageEnums.EDIT_INCOME_DRAWDOWN:
                        return AbrdnSIPPEditIncomeDrawdownDetailsWizard(self.webdriver)
                    case _:
                        return SinglePaymentWarningMessagePage(self.webdriver)
            case PageEnums.ABRDN_JSIPP | PageEnums.ABERDEEN_JSIPP:
                match optionName:
                    case PageEnums.BUY:
                        return ABRDNJSIPPBuyOrderSetupPage(self.webdriver)
                    case PageEnums.SELL:
                        return ABERDEENJSIPPSellOrderSetupPage(self.webdriver)
                    case PageEnums.ADD_REGULAR_PAYMENT:
                        from TestPages.Wizards.ProductWizards.AbrdnJSIPPPaymentsInWizard import AbrdnJSIPPPaymentsInWizard
                        return AbrdnJSIPPPaymentsInWizard(self.webdriver)
                    case PageEnums.EDIT_REGULAR_PAYMENT:
                        from TestPages.Wizards.ProductWizards.AbrdnJSIPPPaymentsInWizard import AbrdnJSIPPPaymentsInWizard
                        return AbrdnJSIPPPaymentsInWizard(self.webdriver)

    @retry(exceptions=UIException, delay=2, tries=5)
    def selectOption(self, optionName, requiredPageToOpen: str = None):
        # optionToSelect = [k for k in self.availableOptions if k.text == optionName]
        optionToSelect = [k for k in self.availableOptions if optionName in k.text]
        if optionToSelect:
            PrintMessage(f"Selecting '{optionName}' option", inStepMessage=True)
            optionToSelect[0].click()
            optionName = optionName if not requiredPageToOpen else requiredPageToOpen
            return self.getPage(optionName)
        raise UIException(f"Option '{optionName}' not found, available options are: {[k.text for k in self.availableOptions]}")

    @property
    def availableOptions(self):
        return manufacture(Button, self.webdriver, self.element, By.XPATH, ".//a[@class='item']")
