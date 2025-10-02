
from StandAlone.DataInsertionPOC.ProcessDataBase import ProcessDataBase
from StandAlone.DataInsertionPOC.ProcessDataHelpers import addToListSkipDuplicates, getValueForKeyCaseInsensitive
from TestPages import DataEnums, PageEnums


class ProcessDataSIPP(ProcessDataBase):
    def _getDstSIPPProductTransfersInAndInvestments(self, sourceProductData: dict):
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
        allInvestmentSelections = {}
        allManagedPortfolioHoldingsSelection = []
        dstProductTransfersIn = []
        sourceTransfersInData: dict
        for sourceTransfersInData in getValueForKeyCaseInsensitive(moneyInData, "Transfers", []):
            conccurrencyData: dict = getValueForKeyCaseInsensitive(sourceTransfersInData, "Conccurrency", {})

            srcInvestmentStrategyData = self._getDstInvestmentStrategyForRef(getValueForKeyCaseInsensitive(sourceProductData, "ProductInvestmentStrategy", []),
                                                                             getValueForKeyCaseInsensitive(sourceTransfersInData, "investmentStrategyToBeUsed", ""))

            # This only for transfer InSpecie (ALEX TO CONFIRM)
            if getValueForKeyCaseInsensitive(sourceTransfersInData, "transferinspecie", "") in PageEnums.YES_CHOICE:
                # This will get recalculated from funds
                cashTransfer = None
            else:
                cashTransfer = getValueForKeyCaseInsensitive(sourceTransfersInData, "estimatedTransferBalance", "")

                if getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "FundHoldings", []):
                    # prep for fund selection on Investments Page
                    dstSelection, dstAllocations = self._getDstHoldingsFromInvestmentStrategy(srcInvestmentStrategyData, paymentType="Transfer")
                    addToListSkipDuplicates(allFundHoldingsSelection, dstSelection)
                    addToListSkipDuplicates(allDstAllocations, dstAllocations)

                if getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "managedPortfolioHoldings", []):
                    managedPortfolioHoldings = getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "managedPortfolioHoldings", [])
                    dstSelection, dstAllocations = self._getDstManagedPortfoliosHoldings(managedPortfolioHoldings,
                                                                                         allocationFieldName="Transfer",
                                                                                         productType=getValueForKeyCaseInsensitive(sourceProductData, "productType", ""))
                    addToListSkipDuplicates(allManagedPortfolioHoldingsSelection, dstSelection)
                    addToListSkipDuplicates(allDstAllocations, dstAllocations)

            transfer = {
                # ALEX CLARIFIED use estimatedTransferBalance for both, but not when In Specie, this will get calculated from funds
                # Transfer: S&S ISA > CASH
                DataEnums.TRANSFER_EST_TRANSFER_VALUE: cashTransfer,

                # * Provider
                DataEnums.TRANSFER_CEDING_SCHEME: getValueForKeyCaseInsensitive(sourceTransfersInData, "cedingProvider", ""),

                # * Plan Number
                DataEnums.TRANSFER_PLAN_NUMBER: getValueForKeyCaseInsensitive(sourceTransfersInData, "planNumber", ""),

                # # This only for transfer InSpecie (ALEX TO CONFIRM)
                # * Existing Pension Type to be transferred in
                DataEnums.TRANSFER_EXISTING_PENSION_TYPE: getValueForKeyCaseInsensitive(sourceTransfersInData, "existingPensionTypeToBeTransferred", ""),

                # TODO: not avialable in data: value: Flexible, Capped
                # Default to flexible as per Lisa T.
                DataEnums.TRANSFER_IS_PLAN_DRAWDOWN: getValueForKeyCaseInsensitive(sourceTransfersInData, "planDrawdown", PageEnums.FLEXIBLE),

                # SIPP specific data
                DataEnums.SIPP_TRANSFER_DATA: {
                    DataEnums.PAYMENT_MADE_FROM_OTHER_PENSION_DEATH_BENEFITS: getValueForKeyCaseInsensitive(sourceTransfersInData, "transferType", ""),
                    DataEnums.MEMBER_OF_EMPLOYER_APPROVED_SCHEME: getValueForKeyCaseInsensitive(conccurrencyData, "memberOfEmployersApprovedScheme", ""),
                    DataEnums.OPTED_OUT_EMPLOYER_APPROVED_SCHEME: getValueForKeyCaseInsensitive(conccurrencyData,
                                                                                                "optedOutorPlanningToOptOutOfEmployersApprovedScheme", ""),
                    DataEnums.CHOSEN_NOT_TO_JOIN_APPROVED_SCHEME: getValueForKeyCaseInsensitive(conccurrencyData, "chosenNotToJoinApprovedScheme", ""),
                    DataEnums.PENSION_DRAWDOWN_REQUIRED: getValueForKeyCaseInsensitive(sourceTransfersInData, "pensionDrawdownRequired", "")
                }
            }

            # SIPP, options PRE or POST
            transfer[DataEnums.TRANSFER_TYPE_PENSION] = getValueForKeyCaseInsensitive(sourceTransfersInData, "pensiontransferType", "")
            transfer[DataEnums.TRANSFER_PENSION_SHARING_ORDER] = getValueForKeyCaseInsensitive(sourceTransfersInData, "pensionSharingOrder", "")
            transfer[DataEnums.TRANSFER_ORDER_RELATE_TO_PAYMENT] = getValueForKeyCaseInsensitive(sourceTransfersInData, "didOrderRelateToPensionInPayment", "")

            dstProductTransfersIn.append(transfer)

        if allFundHoldingsSelection:
            allInvestmentSelections[DataEnums.FUND_HOLDINGS] = allFundHoldingsSelection
        if allManagedPortfolioHoldingsSelection:
            allInvestmentSelections[DataEnums.MANAGED_PORTFOLIOS] = allManagedPortfolioHoldingsSelection

        return dstProductTransfersIn, allDstAllocations, allInvestmentSelections

    def _getSIPPPayments(self, sourceProductData):
        """
        No onshore / offshore as those cannot be transfered (Alex, 12/05/2025)
        """
        moneyInData = getValueForKeyCaseInsensitive(sourceProductData, "MoneyIn", {})
        if not moneyInData:
            return [], [], []

        dstProductPaymentsIn = []
        allDstAllocations = []
        allInvestmentSelections = {}
        allFundHoldings = []
        allManagedPortfolioHoldingsSelection = []
        sourcePaymentsInData: dict

        dstProductPaymentsIn = {}
        dstProductPaymentsIn = []
        sourcePaymentsInData: dict = {}
        for sourcePaymentsInData in getValueForKeyCaseInsensitive(moneyInData, "PaymentsIn", []):
            payment = {
                DataEnums.PAYMENT_TYPE: getValueForKeyCaseInsensitive(sourcePaymentsInData, "paymentType", ""),
                DataEnums.CONTRIBUTOR: getValueForKeyCaseInsensitive(sourcePaymentsInData, "contributer", ""),
                DataEnums.AMOUNT: getValueForKeyCaseInsensitive(sourcePaymentsInData, "amount", ""),
                # DataEnums.ONSHORE_AMOUNT: getValueForKeyCaseInsensitive(sourcePaymentsInData, "onbAmount", ""),
                # DataEnums.OFFSHORE_AMOUNT: getValueForKeyCaseInsensitive(sourcePaymentsInData, "ofbAmount", ""),
                DataEnums.PAYMENT_METHOD: self._getDstPaymentMethod(sourcePaymentsInData),
                DataEnums.PAYMENT_FREQUENCY: getValueForKeyCaseInsensitive(sourcePaymentsInData, "paymentFrequency", ""),
                DataEnums.PAYMENT_SOURCE: getValueForKeyCaseInsensitive(sourcePaymentsInData, "pensionFundsSource", ""),
                DataEnums.CONTINUE_UNTIL: getValueForKeyCaseInsensitive(sourcePaymentsInData, "continueUntil", ""),
                DataEnums.SOURCE_OF_FUNDS: getValueForKeyCaseInsensitive(sourcePaymentsInData, "SourceOfFunds", ""),
                DataEnums.COUNTRY_OF_ORIGIN: getValueForKeyCaseInsensitive(sourcePaymentsInData, "CountryOfOrigin", ""),

                # for SinglePayment > Payment Date - take PaymentFromDate, source: Mark Donaldson
                DataEnums.PAYMENT_DATE: getValueForKeyCaseInsensitive(sourcePaymentsInData, "paymentFromDate", ""),
                DataEnums.PAYMENT_TO_DATE: getValueForKeyCaseInsensitive(sourcePaymentsInData, "paymentToDate", ""),
                DataEnums.PAYMENT_FROM_DATE: getValueForKeyCaseInsensitive(sourcePaymentsInData, "paymentFromDate", ""),
                DataEnums.PAYMENTS_TO_INCREASE: getValueForKeyCaseInsensitive(sourcePaymentsInData, "paymentsToIncrease", "")
            }
            dstProductPaymentsIn.append(payment)

        srcInvestmentStrategyData = self._getDstInvestmentStrategyForRef(getValueForKeyCaseInsensitive(sourceProductData, "ProductInvestmentStrategy", []),
                                                                         getValueForKeyCaseInsensitive(sourcePaymentsInData, "investmentStrategyToBeUsed", ""))

        paymentType = getValueForKeyCaseInsensitive(sourcePaymentsInData, "paymentType", "")
        if getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "FundHoldings", []):
            fundHoldings, dstAllocations = self._getDstHoldingsFromInvestmentStrategy(srcInvestmentStrategyData, paymentType=paymentType, productType=DataEnums.PRODUCT_SIPP)
            addToListSkipDuplicates(allFundHoldings, fundHoldings)
            addToListSkipDuplicates(allDstAllocations, dstAllocations)

        if getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "managedPortfolioHoldings", []):
            managedPortfolioHoldings = getValueForKeyCaseInsensitive(srcInvestmentStrategyData, "managedPortfolioHoldings", [])
            dstSelection, dstAllocations = self._getDstManagedPortfoliosHoldings(managedPortfolioHoldings,
                                                                                 allocationFieldName=paymentType,
                                                                                 productType=getValueForKeyCaseInsensitive(sourceProductData, "productType", ""))
            addToListSkipDuplicates(allManagedPortfolioHoldingsSelection, dstSelection)
            addToListSkipDuplicates(allDstAllocations, dstAllocations)

        if allFundHoldings:
            allInvestmentSelections[DataEnums.FUND_HOLDINGS] = allFundHoldings
        if allManagedPortfolioHoldingsSelection:
            allInvestmentSelections[DataEnums.MANAGED_PORTFOLIOS] = allManagedPortfolioHoldingsSelection

        return dstProductPaymentsIn, allDstAllocations, allInvestmentSelections

    def getSIPPProduct(self, sourceProductData: dict):
        dstPayments, dstPaymentAllocations, dstPaymentInvestmentSelection = self._getSIPPPayments(sourceProductData)
        dstTransfers, dstTransferAllocations, dstTransferInvestmentSelection = self._getDstSIPPProductTransfersInAndInvestments(sourceProductData)

        # Combine Payment & Cash Transfer into single investment selection
        dstInvestments = {DataEnums.INVESTMENT_SELECTION: {}}
        dstInvestments[DataEnums.INVESTMENT_SELECTION].update(dstPaymentInvestmentSelection)
        dstInvestments[DataEnums.INVESTMENT_SELECTION].update(dstTransferInvestmentSelection)

        dstInvestments[DataEnums.ALLOCATIONS] = []
        addToListSkipDuplicates(dstInvestments[DataEnums.ALLOCATIONS], dstPaymentAllocations)
        addToListSkipDuplicates(dstInvestments[DataEnums.ALLOCATIONS], dstTransferAllocations)
        dstInvestments[DataEnums.DISTRIBUTION_OPTION] = self._getDistributionOption(sourceProductData)

        additionalProductDetails = getValueForKeyCaseInsensitive(sourceProductData, "additionalProductDetails", {})

        return {
            # DataEnums.PRODUCT_TYPE: DataEnums.PRODUCT_SIPP,
            DataEnums.PRODUCT_TYPE: DataEnums.PRODUCT_ABRDN_SIPP,
            DataEnums.REGULAR_WITHDRAWALS: getValueForKeyCaseInsensitive(sourceProductData, "regularWithdrawals", ""),
            DataEnums.OPTED_OUT_EMPLOYER_APPROVED_SCHEME: getValueForKeyCaseInsensitive(sourceProductData, "optedOutEmployerPensionContributions", ""),
            DataEnums.RETIREMENT_AGE: getValueForKeyCaseInsensitive(sourceProductData, "retirementAge", ""),
            DataEnums.PAYMENTS_IN: dstPayments,
            DataEnums.TRANSFERS_IN: dstTransfers,
            DataEnums.ADVISOR_CHARGES: self._getDstProductCharges(sourceProductData),
            DataEnums.INVESTMENTS: dstInvestments,
            DataEnums.ADDITIONAL_PRODUCT_DETAILS: {
                DataEnums.ASSUMED_SIPP_BOND_HOLDINGS: getValueForKeyCaseInsensitive(additionalProductDetails, "assumedSIPPBondHoldings", "")}}
