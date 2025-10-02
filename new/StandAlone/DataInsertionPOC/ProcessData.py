"""
File to process generic client data into something PyStorm can utilise

Incoming source data (DICTIONARY) -> Outgoing destination data
"""

from CommonCode.CustomExceptions import DataException
from StandAlone.DataInsertionPOC.ProcessDataBase import ProcessDataBase
from StandAlone.DataInsertionPOC.ProcessDataHelpers import addToListSkipDuplicates, getValueForKeyCaseInsensitive
from StandAlone.DataInsertionPOC.ProcessDataSIPP import ProcessDataSIPP
from TestPages import DataEnums, PageEnums


def processDataIntoClientObject(sourceDataSets: list):
    dstDataSets = []

    for sourceDataSet in sourceDataSets:
        accountData: AccountDataJSON = AccountDataJSON(sourceDataSet["Client"])

        # sanity test
        accountData._getDstProducts()
        dstDataSets.append(accountData)
    return dstDataSets


class AccountDataJSON(ProcessDataBase):
    _clientsData = None
    _productsData = None
    _wrapperData = None
    _bankData = None

    def __init__(self, clientJson: dict):
        self.clientJson: dict = clientJson

    def _getSIPPSourceOfWealth(self):
        srcSourceOfWealth: str = getValueForKeyCaseInsensitive(self.clientJson, "sourceOfWealth", "")
        if "employment" in srcSourceOfWealth.lower():
            return PageEnums.EMPLOYER
        return srcSourceOfWealth

    def _getDstAdviceType(self):
        firstAccountDetails = getValueForKeyCaseInsensitive(self.clientJson, "Account", [])[0]
        srcAdviceType = getValueForKeyCaseInsensitive(firstAccountDetails, "adviceType", defaultValue="").lower()
        match srcAdviceType:
            case "discretionary":
                return PageEnums.DISCRETIONARY
            case "non-discretionary":
                return PageEnums.NonDiscretionary
            case _:
                raise DataException(f"Uknown advice type: {srcAdviceType}")

    def _getDstDisinvestmentStrategy(self):
        firstAccountDetails = getValueForKeyCaseInsensitive(self.clientJson, "Account", [])[0]
        srcDisStrategy = getValueForKeyCaseInsensitive(firstAccountDetails, "disinvestmentStrategy", defaultValue="").lower()
        match srcDisStrategy:
            case "proportional":
                return PageEnums.PROPORTIONAL
            case _:
                raise DataException(f"Uknown disinvestment strategy: {srcDisStrategy}")

    def _processSourceProductToProductData(self, sourceProductData: dict) -> list:
        productType = getValueForKeyCaseInsensitive(sourceProductData, "ProductType", defaultValue="").lower()
        if productType == DataEnums.PRODUCT_ISA.lower():
            return self._getISAPPProduct(sourceProductData, DataEnums.PRODUCT_ISA)

        if productType == DataEnums.PRODUCT_CASH.lower():
            return self._getISAPPProduct(sourceProductData, DataEnums.PRODUCT_CASH)

        if productType in ["personalportfolio", "personal portfolio"]:
            return self._getISAPPProduct(sourceProductData, DataEnums.PRODUCT_PP)

        if productType == DataEnums.PRODUCT_ABRDN_SIPP.lower():
            return ProcessDataSIPP().getSIPPProduct(sourceProductData)

        if productType == DataEnums.PRODUCT_ONSHORE_BOND.lower():
            return self._getOnShoreBondProduct(sourceProductData)

        if productType == DataEnums.PRODUCT_OFFSHORE_BOND.lower():
            return self._getOffShoreBondProduct(sourceProductData)

        return []

    def _getClientType(self):
        advisorData: dict = getValueForKeyCaseInsensitive(self.clientJson, "Adviser", {})
        adviserName: str = getValueForKeyCaseInsensitive(advisorData, "adviserName", "")
        adviserName = adviserName if adviserName else getValueForKeyCaseInsensitive(
            advisorData, "adviserFirstName", "") + getValueForKeyCaseInsensitive(advisorData, "adviserSurname", "")

        return {DataEnums.NETWORK: None,
                DataEnums.FIRM: getValueForKeyCaseInsensitive(advisorData, "firmName", ""),
                DataEnums.ADVISER: adviserName,
                DataEnums.CLIENT_TYPE: getValueForKeyCaseInsensitive(self.clientJson, "clientType", PageEnums.INDIVIDUAL)
                }

    def _getClientEvidenceFolderName(self):
        """
        returns client's first & last name for evidence screenshot
        """
        import re
        from CommonCode.TestHelpers.DateMethods import getTimeStamp
        clientDetails = self._getClientDetails()
        textValue = getValueForKeyCaseInsensitive(clientDetails, DataEnums.FIRST_NAME, "") + getValueForKeyCaseInsensitive(clientDetails, DataEnums.SURNAME, "")
        cleanTextValue = re.sub(r'[^a-zA-Z0-9]', "", textValue)
        return f"{cleanTextValue}_{getTimeStamp()}"

    def _getClientDetails(self):
        contactDetails = getValueForKeyCaseInsensitive(self.clientJson, "ContactDetails", {})
        return {DataEnums.TITLE: getValueForKeyCaseInsensitive(self.clientJson, "title", ""),
                DataEnums.FIRST_NAME: getValueForKeyCaseInsensitive(self.clientJson, "firstNames", ""),
                DataEnums.SURNAME: getValueForKeyCaseInsensitive(self.clientJson, "surname", ""),
                DataEnums.DOB: getValueForKeyCaseInsensitive(self.clientJson, "dateOfBirth", ""),
                DataEnums.GENDER: PageEnums.FEMALE if "F" in getValueForKeyCaseInsensitive(self.clientJson, "gender", "") else PageEnums.MALE,
                DataEnums.EMAIL_ADDRESS: getValueForKeyCaseInsensitive(contactDetails, "emailAddress", ""),
                DataEnums.MOBILE_NUMBER: getValueForKeyCaseInsensitive(contactDetails, "mobileNumber", ""),
                DataEnums.LANDLINE_NUMBER: getValueForKeyCaseInsensitive(contactDetails, "homeNumber", ""),
                DataEnums.NATIONAL_INSURANCE_NUMBER: getValueForKeyCaseInsensitive(self.clientJson, "nationalInsuranceNumber", ""),
                DataEnums.MARITAL_STATUS: getValueForKeyCaseInsensitive(self.clientJson, "maritalStatus", ""),
                DataEnums.TAX_RESIDENCY_OUTSIDE_UK: getValueForKeyCaseInsensitive(self.clientJson, "taxResidencyOtherThanUK", ""),
                DataEnums.NATIONALITIES: self._getDstNationalities(),
                DataEnums.EMPLOYMENT_STATUS: self._getDstEmploymentStatus(),
                DataEnums.BANK_ACCOUNTS: getValueForKeyCaseInsensitive(self.clientJson, "BankAccounts", []),
                DataEnums.ADDRESS: self._getDstAddresses(),

                # # OPP new fields
                DataEnums.COUNTRY_OF_BIRTH: getValueForKeyCaseInsensitive(self.clientJson, "countryOfBirth"),
                DataEnums.EMPLOYMENT_ROLE: getValueForKeyCaseInsensitive(self.clientJson, "employmentRole"),
                DataEnums.OCCUPATION_INDUSTRY: getValueForKeyCaseInsensitive(self.clientJson, "occupationIndustry"),
                DataEnums.SOURCE_OF_WEALTH_PRIMARY: getValueForKeyCaseInsensitive(self.clientJson, "sourceOfWealthPrimary"),
                DataEnums.COUNTRY_OF_ORIGIN_PRIMARY: getValueForKeyCaseInsensitive(self.clientJson, "countryOfOriginPrimary"),

                # SIPP Wrapper data
                DataEnums.RETIREMENT_AGE: getValueForKeyCaseInsensitive(self.clientJson, "retirementAge"),
                DataEnums.RETIREMENT_DATE: getValueForKeyCaseInsensitive(self.clientJson, "retirementDate"),
                DataEnums.SOURCE_OF_WEALTH: self._getSIPPSourceOfWealth(),
                DataEnums.SALARY: getValueForKeyCaseInsensitive(self.clientJson, "annualSalary")
                }

    def _getDstProducts(self):
        """
        Default to first Account

        sourceProductsData Dict -> List change (28/02)
        From Mark:
        It was deliberate, each product will be under it's own account as that is the way Fnz work with their sub accounts.
        Theoretically the customer could have multiple accounts which also lends to that model which gives us a getcustomer().getAllAccounts()
        for each Account getAllProducts() style approach. For your item just assume the customer will have an account object per product

        """
        dstProducts = []
        sourceAccountData = getValueForKeyCaseInsensitive(self.clientJson, "Account", [])[0]
        sourceProducts = getValueForKeyCaseInsensitive(sourceAccountData, "Product", [])  # it probably should be Products
        for sourceProduct in sourceProducts:
            dstProductData = self._processSourceProductToProductData(sourceProduct)
            dstProducts.append(dstProductData)
        return dstProducts

    def _getDstAddresses(self):
        dstAddresses = []
        for sourceAddress in self.clientJson["Address"]:
            sourceAddressLine1 = getValueForKeyCaseInsensitive(sourceAddress, "addressLine1", "")
            sourceAddressLine2 = getValueForKeyCaseInsensitive(sourceAddress, "addressLine2", "")
            sourceAddressLine3 = getValueForKeyCaseInsensitive(sourceAddress, "addressLine3", "")
            sourceTown = getValueForKeyCaseInsensitive(sourceAddress, "town", "")

            line2 = sourceAddressLine2 if sourceAddressLine2 else sourceTown
            if sourceAddressLine3:
                line3 = sourceAddressLine3
            elif sourceTown and sourceTown not in line2:
                line3 = sourceTown
            else:
                line3 = None

            dstAddresses.append({
                DataEnums.ADDRESS_LINE_1: sourceAddressLine1,
                DataEnums.ADDRESS_LINE_2: line2,
                DataEnums.ADDRESS_LINE_3: line3,
                DataEnums.POST_CODE: getValueForKeyCaseInsensitive(sourceAddress, "postCode", ""),
                DataEnums.COUNTRY: getValueForKeyCaseInsensitive(sourceAddress, "country", ""),
                DataEnums.PRIMARY_CORRESPONDENCE_ADDRESS: getValueForKeyCaseInsensitive(sourceAddress, "primaryCorrespondenceAddress", ""),
            })
        return dstAddresses

    def _getDstEmploymentStatus(self):
        sourceDataOccupation = getValueForKeyCaseInsensitive(self.clientJson, "employmentStatus", "")
        match sourceDataOccupation:
            case "Retired":
                return PageEnums.PENSIONER
            case _:
                return sourceDataOccupation

    def _getDstNationalities(self):
        sourceNationalitiesData = getValueForKeyCaseInsensitive(self.clientJson, "nationality", [])
        dstNationalities = []
        for sourceNationality in sourceNationalitiesData:
            dstNationalities.append({
                DataEnums.NATIONALITY: getValueForKeyCaseInsensitive(sourceNationality, "nationality", ""),
                DataEnums.CLIENT_PRIMARY_CITIZENSHIP: PageEnums.YES,
            })
        return dstNationalities

    def _getOnShoreBondProduct(self, sourceProductData: dict):
        # Fund holdings
        investments = self._getBondDstHoldings(sourceProductData, DataEnums.PRODUCT_ONSHORE_BOND)

        # TODO: Model Portofilio
        # investments.update(self._getDstBondModelPortfolios())

        # Money in
        paymentsIn = []
        for paymentIn in sourceProductData.get("MoneyIn", {}).get("PaymentsIn", []):
            paymentsIn.append({
                DataEnums.PAYMENT_TYPE: getValueForKeyCaseInsensitive(paymentIn, "paymentType", ""),
                DataEnums.AMOUNT: getValueForKeyCaseInsensitive(paymentIn, "amount", ""),
                DataEnums.PAYMENT_METHOD: getValueForKeyCaseInsensitive(paymentIn, "paymentMethod", ""),
            })

        return {
            DataEnums.PRODUCT_TYPE: getValueForKeyCaseInsensitive(sourceProductData, "ProductType", ""),
            DataEnums.CHOICE_OF_LAW: getValueForKeyCaseInsensitive(sourceProductData, "choiceOfLaw", ""),
            DataEnums.INVESTMENTS: investments,
            DataEnums.PAYMENTS_IN: paymentsIn
        }

    def _getOffShoreBondProduct(self, sourceProductData: dict):
        employmentDetails = None
        if getValueForKeyCaseInsensitive(sourceProductData, "EmploymentDetails", ""):
            sourceEmploymentDetails: dict = getValueForKeyCaseInsensitive(sourceProductData, "EmploymentDetails", "")
            employmentDetails = {DataEnums.OFFSHORE_BASIC_SALARY: getValueForKeyCaseInsensitive(sourceEmploymentDetails, "OffshoreBasicSalary", ""),
                                 DataEnums.OFFSHORE_OCCUPATION: getValueForKeyCaseInsensitive(sourceEmploymentDetails, "OffShoreOccupation", "")
                                 }

        # Fund holdings
        investments = self._getBondDstHoldings(sourceProductData, DataEnums.PRODUCT_OFFSHORE_BOND)

        # Money in
        paymentsIn = []
        for paymentIn in sourceProductData.get("MoneyIn", {}).get("PaymentsIn", []):
            paymentsIn.append({
                DataEnums.PAYMENT_TYPE: getValueForKeyCaseInsensitive(paymentIn, "paymentType", ""),
                DataEnums.AMOUNT: getValueForKeyCaseInsensitive(paymentIn, "amount", ""),
                DataEnums.PAYMENT_METHOD: getValueForKeyCaseInsensitive(paymentIn, "paymentMethod", ""),
            })

        # TODO: Model Portofilio
        # investments.update(self._getDstBondModelPortfolios())

        return {DataEnums.PRODUCT_TYPE: getValueForKeyCaseInsensitive(sourceProductData, "ProductType", ""),
                DataEnums.CHOICE_OF_LAW: getValueForKeyCaseInsensitive(sourceProductData, "choiceOfLaw", ""),
                DataEnums.OFFSHORE_EMPLOYMENT_DETAILS: employmentDetails,
                DataEnums.INVESTMENTS: investments,
                DataEnums.PAYMENTS_IN: paymentsIn
                }

    def _getISAPPProduct(self, sourceProductData: dict, dstProductType: str):
        dstInvestments = {DataEnums.INVESTMENT_SELECTION: {}}
        dstProductData = {DataEnums.PRODUCT_TYPE: dstProductType,
                          DataEnums.REGULAR_WITHDRAWALS: getValueForKeyCaseInsensitive(sourceProductData, "regularWithdrawals", ""),
                          DataEnums.CUSTOM_PP_NAME: getValueForKeyCaseInsensitive(sourceProductData, "customPPName", "")}

        dstPayments, dstPaymentAllocations, dstPaymentInvestmentSelection = self._getDstPaymentsAndInvestments(sourceProductData, dstProductType)
        dstProductData[DataEnums.PAYMENTS_IN] = dstPayments

        if dstProductType == DataEnums.PRODUCT_ISA:
            dstTransfers, dstTransferAllocations, dstTransferInvestmentSelection = self._getDstProductTransfersInISA(sourceProductData)

        elif dstProductType == DataEnums.PRODUCT_PP:
            dstTransfers, dstTransferAllocations, dstTransferInvestmentSelection = self._getDstProductTransfersInPersonalPortfolio(sourceProductData)

        else:
            dstTransfers = []
            dstTransferInvestmentSelection = []
            dstTransferAllocations = []

        dstProductData[DataEnums.TRANSFERS_IN] = dstTransfers
        dstProductData[DataEnums.ADVISOR_CHARGES] = self._getDstProductCharges(sourceProductData)

        # Combine Payment & Cash Transfer into single investment selection
        dstInvestments[DataEnums.INVESTMENT_SELECTION].update(dstPaymentInvestmentSelection)
        dstInvestments[DataEnums.INVESTMENT_SELECTION].update(dstTransferInvestmentSelection)

        dstInvestments[DataEnums.ALLOCATIONS] = []
        addToListSkipDuplicates(dstInvestments[DataEnums.ALLOCATIONS], dstPaymentAllocations)
        addToListSkipDuplicates(dstInvestments[DataEnums.ALLOCATIONS], dstTransferAllocations)
        dstInvestments[DataEnums.DISTRIBUTION_OPTION] = self._getDistributionOption(sourceProductData)
        dstProductData[DataEnums.INVESTMENTS] = dstInvestments

        return dstProductData

    def _getDstPaymentsAndInvestments(self, sourceProductData, dstProductType):
        """
        Products :
        Personal Portfolio
        ISA
        """
        moneyInData = getValueForKeyCaseInsensitive(sourceProductData, "MoneyIn", {})
        if not moneyInData:
            return [], [], []

        dstProductPaymentsIn = []
        allDstAllocations = []
        allInvestmentSelections = {}
        allExchangeTradedSelection = []
        allFundHoldings = []
        allManagedPortfolioHoldingsSelection = []
        sourcePaymentsInData: dict

        paymentData = getValueForKeyCaseInsensitive(moneyInData, "PaymentsIn", [])
        for sourcePaymentsInData in paymentData:
            payment = {
                DataEnums.PAYMENT_TYPE: getValueForKeyCaseInsensitive(sourcePaymentsInData, "paymentType", ""),
                DataEnums.CONTRIBUTOR: getValueForKeyCaseInsensitive(sourcePaymentsInData, "contributer", ""),
                DataEnums.AMOUNT: getValueForKeyCaseInsensitive(sourcePaymentsInData, "amount", ""),
                # DataEnums.ONSHORE_AMOUNT: getValueForKeyCaseInsensitive(sourcePaymentsInData, "onbAmount", ""),
                # DataEnums.OFFSHORE_AMOUNT: getValueForKeyCaseInsensitive(sourcePaymentsInData, "ofbAmount", ""),
                DataEnums.PAYMENT_METHOD: self._getDstPaymentMethod(sourcePaymentsInData),
                DataEnums.PAYMENT_FREQUENCY: getValueForKeyCaseInsensitive(sourcePaymentsInData, "paymentFrequency", ""),
                DataEnums.BANK_ACCOUNT_REFERENCE: getValueForKeyCaseInsensitive(sourcePaymentsInData, "bankAccountReference", ""),
                DataEnums.PAYMENT_SOURCE: getValueForKeyCaseInsensitive(sourcePaymentsInData, "pensionFundsSource", ""),
                DataEnums.CONTINUE_UNTIL: getValueForKeyCaseInsensitive(sourcePaymentsInData, "continueUntil", ""),

                # # OPP new fields
                DataEnums.SOURCE_OF_FUNDS: getValueForKeyCaseInsensitive(sourcePaymentsInData, "sourceOfFunds", ""),
                DataEnums.COUNTRY_OF_ORIGIN: getValueForKeyCaseInsensitive(sourcePaymentsInData, "countryOfOrigin", ""),

                # for SinglePayment > Payment Date - take PaymentFromDate, source: Mark Donaldson
                DataEnums.PAYMENT_DATE: getValueForKeyCaseInsensitive(sourcePaymentsInData, "paymentFromDate", ""),
                DataEnums.PAYMENT_TO_DATE: getValueForKeyCaseInsensitive(sourcePaymentsInData, "paymentToDate", ""),
                DataEnums.PAYMENT_FROM_DATE: getValueForKeyCaseInsensitive(sourcePaymentsInData, "paymentFromDate", ""),
                DataEnums.PAYMENTS_TO_INCREASE: getValueForKeyCaseInsensitive(sourcePaymentsInData, "paymentsToIncrease", "")
            }

            srcInvestmentStrategyData = self._getDstInvestmentStrategyForRef(getValueForKeyCaseInsensitive(sourceProductData, "ProductInvestmentStrategy", []),
                                                                             getValueForKeyCaseInsensitive(sourcePaymentsInData, "investmentStrategyToBeUsed", ""))

            paymentType = getValueForKeyCaseInsensitive(sourcePaymentsInData, "paymentType", "")
            if getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "FundHoldings", []):
                fundHoldings, dstAllocations = self._getDstHoldingsFromInvestmentStrategy(srcInvestmentStrategyData, paymentType=paymentType, productType=dstProductType)
                addToListSkipDuplicates(allFundHoldings, fundHoldings)
                addToListSkipDuplicates(allDstAllocations, dstAllocations)

            if getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "EquityHoldings", []):
                dstSelection, dstAllocations = self._getDstHoldingsFromInvestmentStrategy(
                    srcInvestmentStrategyData, paymentType="Transfer", holdingsType="EquityHoldings")
                addToListSkipDuplicates(allExchangeTradedSelection, dstSelection)
                addToListSkipDuplicates(allDstAllocations, dstAllocations)

            if getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "managedPortfolioHoldings", []):
                managedPortfolioHoldings = getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "managedPortfolioHoldings", [])
                dstSelection, dstAllocations = self._getDstManagedPortfoliosHoldings(managedPortfolioHoldings,
                                                                                     allocationFieldName=paymentType,
                                                                                     productType=getValueForKeyCaseInsensitive(sourceProductData, "ProductType", ""))
                addToListSkipDuplicates(allManagedPortfolioHoldingsSelection, dstSelection)
                addToListSkipDuplicates(allDstAllocations, dstAllocations)

            dstProductPaymentsIn.append(payment)

        if allFundHoldings:
            allInvestmentSelections[DataEnums.FUND_HOLDINGS] = allFundHoldings
        if allExchangeTradedSelection:
            allInvestmentSelections[DataEnums.EXCHANGE_TRADED] = allExchangeTradedSelection
        if allManagedPortfolioHoldingsSelection:
            allInvestmentSelections[DataEnums.MANAGED_PORTFOLIOS] = allManagedPortfolioHoldingsSelection

        return dstProductPaymentsIn, allDstAllocations, allInvestmentSelections

    def _getDstProductTransfersInISA(self, sourceProductData: dict):
        """
        Investments are organized per investment strategy

        It is expected that
         - Single Payment & Cash & Transfer InSpecie will have same investment strategy
         - Regular Payment will have different investment strategy
        """
        moneyInData: dict = getValueForKeyCaseInsensitive(sourceProductData, "MoneyIn", {})
        if not moneyInData:
            return [], [], []

        allDstAllocations = []
        allFundHoldingsSelection = []
        allExchangeTradedSelection = []
        allInvestmentSelections = {}
        allManagedPortfolioHoldingsSelection = []
        dstProductTransfersIn = []
        sourceTransfersInData: dict
        for sourceTransfersInData in getValueForKeyCaseInsensitive(moneyInData, "Transfers", []):
            sourceSubInTransfer = getValueForKeyCaseInsensitive(sourceTransfersInData, "subscriptionsIncludedInTheTransfer", defaultValue="").lower()
            match sourceSubInTransfer:
                case "current":
                    subInTransfer = PageEnums.TRANSFER_SUB_CURRENT
                case "non_current":
                    subInTransfer = PageEnums.TRANSFER_SUB_NON_CURRENT
                case "both":
                    subInTransfer = PageEnums.TRANSFER_SUB_BOTH
                case _:
                    subInTransfer = ""

            srcInvestmentStrategyData = self._getDstInvestmentStrategyForRef(getValueForKeyCaseInsensitive(sourceProductData, "ProductInvestmentStrategy", []),
                                                                             getValueForKeyCaseInsensitive(sourceTransfersInData, "investmentStrategyToBeUsed", ""))

            dstTransfer = {
                DataEnums.TRANSFER_CEDING_SCHEME: getValueForKeyCaseInsensitive(sourceTransfersInData, "cedingProvider", ""),

                # Existing ISA account number
                DataEnums.TRANSFER_PLAN_NUMBER: getValueForKeyCaseInsensitive(sourceTransfersInData, "planNumber", ""),

                # Subscriptions included in the transfer
                DataEnums.TRANSFER_SUB_INCLUDED: subInTransfer,

                # As per Alex instructions, one subscription can be done and so for transfer its taken from firstSubscriptionTYE.
                # Expected to have only one
                # Date of first subscription
                DataEnums.TRANSFER_DATE_OF_FIRST_SUBSCRIPTION: getValueForKeyCaseInsensitive(sourceProductData, "firstSubscriptionTYE", ""),
            }

            # Transfer Type: S&S ISA
            if getValueForKeyCaseInsensitive(sourceTransfersInData, "transferringISAType", "").lower() == DataEnums.TRANSFER_TYPE_SNS_ISA.lower():
                dstTransfer[DataEnums.TRANSFER_TYPE] = getValueForKeyCaseInsensitive(sourceTransfersInData, "transferringISAType", "")

                sourceSubInTransfer = getValueForKeyCaseInsensitive(sourceTransfersInData, "subscriptionsIncludedInTheTransfer", defaultValue="").lower()
                # Subscriptions : Current or Both
                if sourceSubInTransfer in [PageEnums.TRANSFER_SUB_CURRENT, PageEnums.TRANSFER_SUB_BOTH]:
                    print("Subscriptions: current and both")

                    # Transfer from Flexible ISA?

                    # Date of first subscription

                    # Estimated current year subscription (£)

                # Subscriptions : Non-Current
                else:
                    print("Subscriptions: non-current")

                dstTransfer[DataEnums.TRANSFER_INVESTMENTS_IN_SPECIE] = getValueForKeyCaseInsensitive(sourceTransfersInData, "transferinspecie", "")

                # IN SPECIE
                if getValueForKeyCaseInsensitive(sourceTransfersInData, "transferinspecie", "") in PageEnums.YES_CHOICE:
                    # Assets to be re-registered

                    # # This only for transfer InSpecie (ALEX TO CONFIRM)
                    dstTransfer[DataEnums.INVESTMENTS] = self._getDstTransferInSpecieAssetsToBeReRegistered(srcInvestmentStrategyData)
                    dstTransfer[DataEnums.TRANSFER_CERTIFIED_SHARES_EQUITIES] = getValueForKeyCaseInsensitive(sourceTransfersInData, "transferFromFlexibleISA", "")
                    dstTransfer[DataEnums.TRANSFER_EXISTING_PENSION_TYPE] = getValueForKeyCaseInsensitive(
                        sourceTransfersInData, "existingPensionTypeToBeTransferred", "")

                    # Estimated cash amount being transfered
                    dstTransfer[DataEnums.TRANSFER_EST_TRANSFER_VALUE] = getValueForKeyCaseInsensitive(sourceTransfersInData, "residualCash", "")

                # not IN SPECIE
                else:
                    dstTransfer[DataEnums.TRANSFER_EST_TRANSFER_VALUE] = getValueForKeyCaseInsensitive(sourceTransfersInData, "estimatedTransferBalance", "")

                    if getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "FundHoldings", []):
                        dstSelection, dstAllocations = self._getDstHoldingsFromInvestmentStrategy(
                            srcInvestmentStrategyData, paymentType="Transfer", holdingsType="FundHoldings")
                        addToListSkipDuplicates(allFundHoldingsSelection, dstSelection)
                        addToListSkipDuplicates(allDstAllocations, dstAllocations)

                    if getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "EquityHoldings", []):
                        dstSelection, dstAllocations = self._getDstHoldingsFromInvestmentStrategy(
                            srcInvestmentStrategyData, paymentType="Transfer", holdingsType="EquityHoldings")
                        addToListSkipDuplicates(allExchangeTradedSelection, dstSelection)
                        addToListSkipDuplicates(allDstAllocations, dstAllocations)

                    if getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "managedPortfolioHoldings", []):
                        managedPortfolioHoldings = getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "managedPortfolioHoldings", [])
                        dstSelection, dstAllocations = self._getDstManagedPortfoliosHoldings(
                            managedPortfolioHoldings, allocationFieldName="Transfer", productType=getValueForKeyCaseInsensitive(
                                sourceProductData, "productType", ""))
                        addToListSkipDuplicates(allManagedPortfolioHoldingsSelection, dstSelection)
                        addToListSkipDuplicates(allDstAllocations, dstAllocations)

            # Transfer Type: Cash
            else:
                dstTransfer[DataEnums.TRANSFER_TYPE] = DataEnums.TRANSFER_TYPE_CASH

                # Is this an internal transfer from an existing Wrap Cash ISA?

                # Cash value
                dstTransfer[DataEnums.TRANSFER_CASH_VALUE] = getValueForKeyCaseInsensitive(sourceTransfersInData, "estimatedTransferBalance", "")

            dstProductTransfersIn.append(dstTransfer)

        if allFundHoldingsSelection:
            allInvestmentSelections[DataEnums.FUND_HOLDINGS] = allFundHoldingsSelection
        if allExchangeTradedSelection:
            allInvestmentSelections[DataEnums.EXCHANGE_TRADED] = allExchangeTradedSelection
        if allManagedPortfolioHoldingsSelection:
            allInvestmentSelections[DataEnums.MANAGED_PORTFOLIOS] = allManagedPortfolioHoldingsSelection

        return dstProductTransfersIn, allDstAllocations, allInvestmentSelections

    def _getDstProductTransfersInPersonalPortfolio(self, sourceProductData: dict):
        """
        Investments are organized per investment strategy

        It is expected that
         - Single Payment & Cash & Transfer InSpecie will have same investment strategy
         - Regular Payment will have different investment strategy
        """
        moneyInData: dict = getValueForKeyCaseInsensitive(sourceProductData, "MoneyIn", {})
        if not moneyInData:
            return [], [], []

        allDstAllocations = []
        allFundHoldingsSelection = []
        allExchangeTradedSelection = []
        allInvestmentSelections = {}
        dstProductTransfersIn = []
        sourceTransfersInData: dict
        for sourceTransfersInData in getValueForKeyCaseInsensitive(moneyInData, "Transfers", []):

            # Are there any certificated shares/equities included in the transfer?
            if getValueForKeyCaseInsensitive(moneyInData, "SharesAndEquities", ""):  # TODO: properly hook up
                srcInvestmentStrategyData = self._getDstInvestmentStrategyForRef(getValueForKeyCaseInsensitive(sourceProductData, "ProductInvestmentStrategy", []),
                                                                                 getValueForKeyCaseInsensitive(sourceTransfersInData, "investmentStrategyToBeUsed", ""))

                if getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "FundHoldings", []):
                    dstSelection, dstAllocations = self._getDstHoldingsFromInvestmentStrategy(
                        srcInvestmentStrategyData, paymentType="Transfer", holdingsType="FundHoldings")
                    addToListSkipDuplicates(allFundHoldingsSelection, dstSelection)
                    addToListSkipDuplicates(allDstAllocations, dstAllocations)

                if getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "EquityHoldings", []):
                    dstSelection, dstAllocations = self._getDstHoldingsFromInvestmentStrategy(
                        srcInvestmentStrategyData, paymentType="Transfer", holdingsType="EquityHoldings")
                    addToListSkipDuplicates(allExchangeTradedSelection, dstSelection)
                    addToListSkipDuplicates(allDstAllocations, dstAllocations)
            else:
                print(2)

            dstTransfer = {
                DataEnums.TRANSFER_CEDING_SCHEME: getValueForKeyCaseInsensitive(sourceTransfersInData, "cedingProvider", ""),
            }

            dstTransfer[DataEnums.TRANSFER_PLAN_NUMBER] = getValueForKeyCaseInsensitive(sourceTransfersInData, "planNumber", "")
            # DataEnums.TRANSFER_EST_TRANSFER_VALUE: getValueForKeyCaseInsensitive(sourceTransfersInData, "residualCash", ""),

            # this for account number in PP transfer
            dstTransfer[DataEnums.ACCOUNT_NUMBER_AT_CUSTODIAN] = getValueForKeyCaseInsensitive(sourceTransfersInData, "planNumber", "")
            dstTransfer[DataEnums.TRANSFER_INVESTMENTS_IN_SPECIE] = getValueForKeyCaseInsensitive(sourceTransfersInData, "transferinspecie", "")
            dstTransfer[DataEnums.TRANSFER_INTERNAL_FROM_EXISTING_WRAP] = "no"
            dstTransfer[DataEnums.TRANSFER_LOCATION] = getValueForKeyCaseInsensitive(sourceTransfersInData, "location", "")
            dstTransfer[DataEnums.TRANSFER_EST_CURR_YEAR_SUB] = getValueForKeyCaseInsensitive(sourceTransfersInData, "estimatedISACurrentYearSubscription", "")
            dstTransfer[DataEnums.TRANSFER_FROM_FLEXIBLE_ISA] = getValueForKeyCaseInsensitive(sourceTransfersInData, "transferFromFlexibleISA", "")

            # As per Alex instructions, one subscription can be done and so for transfer its taken from firstSubscriptionTYE.
            # Expected to have only one
            dstTransfer[DataEnums.TRANSFER_DATE_OF_FIRST_SUBSCRIPTION] = getValueForKeyCaseInsensitive(sourceProductData, "firstSubscriptionTYE", "")

            # # # This only for transfer InSpecie (ALEX TO CONFIRM)
            # DataEnums.INVESTMENTS: transferAssets,
            # DataEnums.TRANSFER_CERTIFIED_SHARES_EQUITIES: getValueForKeyCaseInsensitive(sourceTransfersInData, "transferFromFlexibleISA", ""),
            # DataEnums.TRANSFER_EXISTING_PENSION_TYPE: getValueForKeyCaseInsensitive(sourceTransfersInData, "existingPensionTypeToBeTransferred", ""),

            # TODO: not avialable in data: value: Flexible, Capped
            # Default to flexible as per Lisa T.
            dstTransfer[DataEnums.TRANSFER_IS_PLAN_DRAWDOWN] = getValueForKeyCaseInsensitive(sourceTransfersInData, "planDrawdown", PageEnums.FLEXIBLE)

            # TODO: need to specify source of ownership
            dstTransfer[DataEnums.TRANSFER_OWNERSHIP_DETAILS] = {
                DataEnums.TITLE: getValueForKeyCaseInsensitive(self.clientJson, "title", ""),
                DataEnums.FIRST_NAME: getValueForKeyCaseInsensitive(self.clientJson, "firstNames", ""),
                DataEnums.SURNAME: getValueForKeyCaseInsensitive(self.clientJson, "surname", ""),
                DataEnums.DOB: getValueForKeyCaseInsensitive(self.clientJson, "dateOfBirth", ""),
                DataEnums.ADDRESS: self._getDstAddresses()
            }

            dstProductTransfersIn.append(dstTransfer)

        if allFundHoldingsSelection:
            allInvestmentSelections[DataEnums.FUND_HOLDINGS] = allFundHoldingsSelection
        if allExchangeTradedSelection:
            allInvestmentSelections[DataEnums.EXCHANGE_TRADED] = allExchangeTradedSelection

        return dstProductTransfersIn, allDstAllocations, allInvestmentSelections

    def _getDstTransferInSpecieAssetsToBeReRegistered(self, srcInvestmentStrategyData):
        dstInvestmentSelection = {}
        allDstAllocations = []

        dstInvestmentSelection[DataEnums.FUND_HOLDINGS], dstAllocations = self._getDstHoldingsFromInvestmentStrategy(
            srcInvestmentStrategyData, paymentType="Transfer", holdingsType="FundHoldings")
        allDstAllocations.extend(dstAllocations)

        dstInvestmentSelection[DataEnums.EXCHANGE_TRADED], dstAllocations = self._getDstHoldingsFromInvestmentStrategy(
            srcInvestmentStrategyData, paymentType="Transfer", holdingsType="EquityHoldings")
        allDstAllocations.extend(dstAllocations)

        return {DataEnums.INVESTMENT_SELECTION: dstInvestmentSelection,
                DataEnums.ALLOCATIONS: allDstAllocations}

    def _getDstBankAccounts(self):
        sourceBanksData = getValueForKeyCaseInsensitive(self.clientJson, "BankAccounts", [])
        if len(sourceBanksData) == 0:
            return None

        def getSortCode(srcSortCode):
            if len(srcSortCode) == 6:
                return f"{srcSortCode[0:2]}-{srcSortCode[2:4]}-{srcSortCode[4:6]}"
            return srcSortCode

        dstBanksData = []
        for sourceBankData in sourceBanksData:
            dstBankData = {
                DataEnums.ACCOUNT_NAME: getValueForKeyCaseInsensitive(sourceBankData, "accountName", ""),
                DataEnums.SORT_CODE: getSortCode(getValueForKeyCaseInsensitive(sourceBankData, "accountSortCode", "")),
                DataEnums.ACCOUNT_NUMBER: getValueForKeyCaseInsensitive(sourceBankData, "accountNumber", ""),
                DataEnums.DIRECT_DEBIT_INSTRUCTIONS: getValueForKeyCaseInsensitive(sourceBankData, "directDebit", ""),
                DataEnums.DIRECT_DEBIT_SETUP: getValueForKeyCaseInsensitive(sourceBankData, "mandateType", ""),
                DataEnums.ACCOUNT_OWNER: getValueForKeyCaseInsensitive(sourceBankData, "owner", "")
            }
            dstBanksData.append(dstBankData)
        return dstBanksData

    def getProductData(self, productType):
        products = [k for k in self.productsData if getValueForKeyCaseInsensitive(k, DataEnums.PRODUCT_TYPE, "") == productType]
        if products:
            return products[0]
        # quietly or raise?
        return {}

    @property
    def wrapperData(self) -> dict:
        if self._wrapperData is None:
            sourcePref = getValueForKeyCaseInsensitive(self.clientJson, "Preferences", {})
            paperPref = PageEnums.YES if getValueForKeyCaseInsensitive(sourcePref, "goPaperless", defaultValue="").lower() in [
                PageEnums.YES.lower(), "y"] else PageEnums.NO
            sourceAccount = getValueForKeyCaseInsensitive(self.clientJson, "Account", [])[0]

            firstName = getValueForKeyCaseInsensitive(self.clientJson, 'firstNames', '')
            surName = getValueForKeyCaseInsensitive(self.clientJson, 'surname', '')

            self._wrapperData = {
                DataEnums.CLIENT_TYPE: PageEnums.SINGLE,
                DataEnums.PAPERLESS_PREFERENCE: paperPref,
                DataEnums.FINANCIAL_ADVICE: PageEnums.YES,
                DataEnums.SERVICE_PROPOSITION_TYPE: PageEnums.WRAP,
                DataEnums.ADVICE_TYPE: self._getDstAdviceType(),
                DataEnums.ACCOUNT_TYPE: getValueForKeyCaseInsensitive(
                    sourceAccount,
                    "accountType"),
                DataEnums.ACCOUNT_NAME: f"{firstName}{surName}",
                DataEnums.DISINVESTMENT_STRATEGY: self._getDstDisinvestmentStrategy(),
            }
        return self._wrapperData

    @property
    def productsData(self) -> dict:
        if self._productsData is None:
            self._productsData = self._getDstProducts()
        return self._productsData

    @property
    def bankData(self) -> dict:
        if self._bankData is None:
            self._bankData = self._getDstBankAccounts()
        return self._bankData

    @property
    def clientsData(self) -> dict:
        if self._clientsData is None:
            self._clientsData = self._getClientDetails()
        return self._clientsData
