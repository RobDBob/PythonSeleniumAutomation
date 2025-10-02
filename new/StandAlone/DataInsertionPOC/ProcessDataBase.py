from StandAlone.DataInsertionPOC.ProcessDataHelpers import getValueForKeyCaseInsensitive
from TestPages import DataEnums, PageEnums


class ProcessDataBase:
    def _getDstProductCharges(self, sourceProductData):
        srcChargesData = getValueForKeyCaseInsensitive(sourceProductData, "Charges", {})

        dstChargesData = {}
        srcOAC = getValueForKeyCaseInsensitive(srcChargesData, "ongoingAdviserChargeType", defaultValue="").lower()

        match srcOAC:
            case "percentage":
                dstChargesData[DataEnums.OAC_CHARGE_TYPE] = PageEnums.TYPE_PERCENTAGE
            case "monetary":
                dstChargesData[DataEnums.OAC_CHARGE_TYPE] = PageEnums.TYPE_MONETARY
            case _:
                dstChargesData[DataEnums.OAC_CHARGE_TYPE] = srcOAC

        srcIAC = getValueForKeyCaseInsensitive(srcChargesData, "initialAdviserChargeType", defaultValue="").lower()
        match srcIAC:
            case "percentage":
                dstChargesData[DataEnums.IAC_CHARGE_TYPE] = PageEnums.TYPE_PERCENTAGE
            case "monetary":
                dstChargesData[DataEnums.IAC_CHARGE_TYPE] = PageEnums.TYPE_MONETARY
            case _:
                dstChargesData[DataEnums.IAC_CHARGE_TYPE] = srcIAC

        srcOCF = getValueForKeyCaseInsensitive(srcChargesData, "ongoingChargeFrequency", defaultValue="").lower()
        match srcOCF:
            case "monthly":
                dstChargesData[DataEnums.OAC_CHARGE_FREQUENCY] = PageEnums.MONTHLY
            case "quarterly":
                dstChargesData[DataEnums.OAC_CHARGE_FREQUENCY] = PageEnums.Quarterly
            case "halfyearly":
                dstChargesData[DataEnums.OAC_CHARGE_FREQUENCY] = PageEnums.HALFYEARLY
            case "annually":
                dstChargesData[DataEnums.OAC_CHARGE_FREQUENCY] = PageEnums.ANNUALLY
            case _:
                dstChargesData[DataEnums.OAC_CHARGE_FREQUENCY] = srcOCF

        dstChargesData[DataEnums.OAC_CHARGE_AMOUNT] = getValueForKeyCaseInsensitive(srcChargesData, "ongoingChargeAmount", "")
        dstChargesData[DataEnums.IAC_CHARGE_AMOUNT] = getValueForKeyCaseInsensitive(srcChargesData, "initialChargeAmount", "")
        dstChargesData[DataEnums.EXCLUDE_ILLUSTRATION_CHARGES] = getValueForKeyCaseInsensitive(srcChargesData, "excludeChargesFromIllustration", "")

        return dstChargesData

    def _getDstInvestmentStrategyForRef(self, productInvestmentStrategyData: list, investmentStrategyRef: str):
        for investmentData in productInvestmentStrategyData:
            if getValueForKeyCaseInsensitive(investmentData, "strategyReference", defaultValue="").lower() == investmentStrategyRef.lower():
                return investmentData
        return {}

    def _getDistributionOption(self, sourceProductData):
        srcDistributionOption: str = getValueForKeyCaseInsensitive(sourceProductData, "distributionOption", defaultValue="").lower()
        match srcDistributionOption:
            case "reinvest":
                return PageEnums.DISTRIBUTION_REINVEST
            case _:
                return srcDistributionOption.capitalize() if srcDistributionOption else None

    def _getDstPaymentMethod(self, paymentsData):
        sourcePaymentMethod = getValueForKeyCaseInsensitive(paymentsData, "paymentMethod", "")
        match sourcePaymentMethod:
            case "Direct Debit":
                return PageEnums.DIRECT_DEBIT
            case "Direct Credit":
                return PageEnums.DIRECT_CREDIT
            case _:
                return sourcePaymentMethod

    def _getBondDstHoldings(self, sourceProductData, productType=None):
        """
        Bond holdings without SIPP
        """
        allDstSelections = []
        allDstAllocations = []

        for fundHolding in getValueForKeyCaseInsensitive(sourceProductData, "FundHoldings", []):
            investmentName = getValueForKeyCaseInsensitive(fundHolding, "InvestmentName", "")
            fundCodeCodes = ["ISIN", "citiCode", "sedol"]

            fundCodes = [getValueForKeyCaseInsensitive(fundHolding, code) for code in fundCodeCodes if getValueForKeyCaseInsensitive(fundHolding, code, "")]
            if fundCodes:
                fundCode = fundCodes[0]
            elif investmentName == "GBPCash":
                fundCode = "GBPCash"
            else:
                fundCode = None

            # GBPCash is not a fund
            if investmentName != "GBPCash":
                dstSelection = {
                    DataEnums.INVESTMENT_NAME: investmentName,
                    DataEnums.INVESTMENT_CODE: fundCode
                }
                if dstSelection not in allDstSelections:
                    allDstSelections.append(dstSelection)

            dstAllocation = {
                DataEnums.INVESTMENT_NAME: investmentName,
                DataEnums.INVESTMENT_CODE: fundCode,
                DataEnums.ALLOCATION_PERCENTAGE: getValueForKeyCaseInsensitive(fundHolding, "percentageAllocation", ""),
                DataEnums.ALLOCATION_PRODUCT: productType,
            }

            allDstAllocations.append(dstAllocation)

        return {DataEnums.INVESTMENT_SELECTION: {DataEnums.FUND_HOLDINGS: allDstSelections},
                DataEnums.ALLOCATIONS: allDstAllocations}

    def _getDstHoldingsFromInvestmentStrategy(self, srcInvestmentStrategyData, paymentType=None, productType=None, holdingsType="FundHoldings"):
        """
        Method be used by both
         - PaymentsIn > Transfers > InSpecie > Assets to be re-registered
         - Investments

        paymentType: Single, Regular, TransferIn
        productType: SIPP, ISA, Cash
        """
        fundHoldings: list = getValueForKeyCaseInsensitive(srcInvestmentStrategyData, holdingsType, [])
        dstAllocations = []
        dstSelections = []
        for fundHolding in fundHoldings:
            investmentName = getValueForKeyCaseInsensitive(fundHolding, "InvestmentName", "")
            if not investmentName:

                # Test framework moved on to Investment Name for all investment names including funds
                investmentName = getValueForKeyCaseInsensitive(fundHolding, "fundName", "")

            fundCodeCodes = ["ISIN", "citiCode", "sedol"]
            fundCodes = [getValueForKeyCaseInsensitive(fundHolding, code) for code in fundCodeCodes if getValueForKeyCaseInsensitive(fundHolding, code, "")]
            if fundCodes:
                fundCode = fundCodes[0]
            elif investmentName == "GBPCash":
                fundCode = "GBPCash"
            else:
                fundCode = None

            # GBPCash is not a fund
            if investmentName != "GBPCash":
                holding = {
                    DataEnums.INVESTMENT_NAME: investmentName,
                    DataEnums.INVESTMENT_CODE: fundCode
                }
                if holding not in dstSelections:
                    dstSelections.append(holding)

            allocationProduct = getValueForKeyCaseInsensitive(fundHolding, "AllocationProduct", "")
            allocationProduct = allocationProduct if allocationProduct else productType
            dstAllocations.append({
                DataEnums.INVESTMENT_NAME: investmentName,
                DataEnums.INVESTMENT_CODE: fundCode,

                DataEnums.ALLOCATION_PERCENTAGE: getValueForKeyCaseInsensitive(fundHolding, "percentageAllocation", ""),
                DataEnums.INVESTMENT_UNITS: getValueForKeyCaseInsensitive(fundHolding, "units", ""),
                DataEnums.ALLOCATION_FIELD_NAME: paymentType,
                DataEnums.ALLOCATION_PRODUCT: allocationProduct,
                DataEnums.ALLOCATION_TAX_BOOK_COST: getValueForKeyCaseInsensitive(fundHolding, "taxBookCost", ""),
                DataEnums.ALLOCATION_AQUISITION_DATE: getValueForKeyCaseInsensitive(fundHolding, "aquisitiondDate", ""),

                # DataEnums.ONSHORE_ALLOCATION: getValueForKeyCaseInsensitive(fundHolding, "onshoreBondAllocation", ""),
                # DataEnums.OFFSHORE_ALLOCATION: getValueForKeyCaseInsensitive(fundHolding, "offshoreBondAllocation", "")
            })

        return dstSelections, dstAllocations

    def _getDstManagedPortfoliosHoldings(self, managedPortfolioHoldings, allocationFieldName, productType=None):
        dstSelections = []
        dstAllocations = []
        for srcManagedPortfolio in managedPortfolioHoldings:
            portfolioName = getValueForKeyCaseInsensitive(srcManagedPortfolio, "portfolioName", "")

            dstAllocations.append({
                DataEnums.INVESTMENT_NAME: portfolioName,
                DataEnums.ALLOCATION_PERCENTAGE: getValueForKeyCaseInsensitive(srcManagedPortfolio, "percentageAllocation", ""),
                DataEnums.ALLOCATION_FIELD_NAME: allocationFieldName,
                DataEnums.ALLOCATION_PRODUCT: productType
            })

            investmentManager = getValueForKeyCaseInsensitive(srcManagedPortfolio, "investmentManager", "")

            # SIPP setup will require advanced search
            # advancedSearch = bool(investmentManager and productType == DataEnums.PRODUCT_SIPP)
            advancedSearch = bool(investmentManager and productType == DataEnums.PRODUCT_ABRDN_SIPP)
            dstSelections.append({DataEnums.INVESTMENT_NAME: portfolioName,
                                  DataEnums.PORTFOLIO_TYPE: getValueForKeyCaseInsensitive(srcManagedPortfolio, "portfolioType", ""),
                                  DataEnums.INVESTMENT_MANAGER: investmentManager,
                                  DataEnums.ADVANCED_SEARCH: advancedSearch})
        return dstSelections, dstAllocations
