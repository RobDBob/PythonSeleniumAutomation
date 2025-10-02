import re
import traceback
from datetime import datetime
from bs4 import BeautifulSoup
from retry import retry
from CommonCode.API.BackOffice.BackOfficeRequests import BackOfficeRequests
from CommonCode.API.BackOffice.BOEnums import OrderEnum
from CommonCode.API.BackOffice.Data.WrapOrdersData import WrapOrder
from CommonCode.CustomExceptions import APIException
from CommonCode.TestExecute.Logging import PrintMessage


class BackOfficeHelper:
    DATE_FORMAT = "%d-%b-%Y"

    def __init__(self, baseUrl, userName, userPassword):
        self.backOfficeRequests = BackOfficeRequests(baseUrl, userName, userPassword)

    def _getDataTestFill(self, htmlText, batchId):
        todayDate = datetime.now().strftime(BackOfficeHelper.DATE_FORMAT)
        parsedHTML = BeautifulSoup(htmlText, features="html.parser")
        data = {"actiontype": "testdatafill",
                "webauditlogid": self.backOfficeRequests.webAuditLogId,
                "priceDate": parsedHTML.body.find("input", attrs={"id": "priceDate"})["value"],
                "batchId": batchId,
                "SearchFundManagerID": None,
                "SearchOrderID": None,
                "DatePlaced": None,
                "securitytype": None,
                "InstrumentCode": None,
                "Currency": None,
                "SearchEFMDealReference": None,
                "placementMethod": None,
                "BuyOrSell": None,
                "testDataDate": todayDate,
                "testSettlementDate": None,
                "1OrderID": parsedHTML.body.find("input", attrs={"id": "1OrderID"})["value"],
                "1CustodianAccountID": parsedHTML.body.find("input", attrs={"id": "1CustodianAccountID"})["value"],
                "1FilledQuantity": parsedHTML.body.find("input", attrs={"id": "1FilledQuantity"})["value"],
                "1FilledPrice": None,
                "1FilledValueExComm": parsedHTML.body.find("input", attrs={"id": "1FilledValueExComm"})["value"],
                "1DatePriced": parsedHTML.body.find("input", attrs={"id": "1DatePriced"})["value"],
                "1SettlementDate": parsedHTML.body.find("input", attrs={"id": "1SettlementDate"})["value"],
                "1FXRate": 1,
                "1Fee_EFMDilutionLevy": parsedHTML.body.find("input", attrs={"id": "1Fee_EFMDilutionLevy"})["value"],
                "1Fee_EFMInitialCharge": parsedHTML.body.find("input", attrs={"id": "1Fee_EFMInitialCharge"})["value"],
                "1UT_InitialCharge": parsedHTML.body.find("input", attrs={"id": "1UT_InitialCharge"})["value"],
                "1UT_Discount": parsedHTML.body.find("input", attrs={"id": "1UT_Discount"})["value"],
                "1EFMDealReference": None}
        return data

    def _getDataFillSave(self, htmlText, batchId):
        todayDate = datetime.now().strftime(BackOfficeHelper.DATE_FORMAT)
        parsedHTML = BeautifulSoup(htmlText, features="html.parser")
        data = {"actiontype": "save",
                "webauditlogid": self.backOfficeRequests.webAuditLogId,
                "priceDate": parsedHTML.body.find("input", attrs={"id": "priceDate"})["value"],
                "batchId": batchId,
                "SearchFundManagerID": None,
                "SearchOrderID": None,
                "DatePlaced": None,
                "securitytype": None,
                "InstrumentCode": None,
                "Currency": None,
                "SearchEFMDealReference": None,
                "placementMethod": None,
                "BuyOrSell": None,
                "testDataDate": None,
                "testSettlementDate": todayDate,
                "1OrderID": parsedHTML.body.find("input", attrs={"id": "1OrderID"})["value"],
                "1CustodianAccountID": parsedHTML.body.find("input", attrs={"id": "1CustodianAccountID"})["value"],
                "1FilledQuantity": parsedHTML.body.find("input", attrs={"id": "1FilledQuantity"})["value"],
                "1FilledPrice": parsedHTML.body.find("input", attrs={"id": "1FilledPrice"})["value"],
                "1FilledValueExComm": parsedHTML.body.find("input", attrs={"id": "1FilledValueExComm"})["value"],
                "1DatePriced": parsedHTML.body.find("input", attrs={"id": "1DatePriced"})["value"],
                "1SettlementDate": todayDate,
                "1FXRate": 1,
                "1Fee_EFMDilutionLevy": parsedHTML.body.find("input", attrs={"id": "1Fee_EFMDilutionLevy"})["value"],
                "1Fee_EFMInitialCharge": parsedHTML.body.find("input", attrs={"id": "1Fee_EFMInitialCharge"})["value"],
                "1UT_InitialCharge": parsedHTML.body.find("input", attrs={"id": "1UT_InitialCharge"})["value"],
                "1UT_Discount": parsedHTML.body.find("input", attrs={"id": "1UT_Discount"})["value"],
                "1EFMDealReference": None}
        return data

    def _getDataPooledCompletionIndex(self, parsedHTML, batchId):
        """
        Returns table index for expected data
        """
        idLocatorName = "OrderID"
        # there might be multiple orders awaiting completion, need to identify ours

        for dataRow in parsedHTML.body.find_all("tr", attrs={"class": "RowOver"}):
            orderElement = dataRow.find("input", id=lambda id: id and idLocatorName in id)
            pooledOrderDetails = self.backOfficeRequests.getPooledOrderDetails(orderElement["value"])
            if pooledOrderDetails.isBatchIdOnUnderlyingOrders(batchId):
                return re.match(fr"(\d){idLocatorName}", orderElement["name"]).group(1)
        return None

    def _getDataPooledCompletionForSAVE(self, htmlText, batchId):
        """
        Data displayed on the table is indexed
        We'll need to identify index prior to selecting specific deal to close
        """
        parsedHTML = BeautifulSoup(htmlText, features="html.parser")
        locatorIndex = self._getDataPooledCompletionIndex(parsedHTML, batchId)

        data = {"actiontype": "save",
                "webauditlogid": self.backOfficeRequests.webAuditLogId,
                "priceDate": None,
                "SearchFundManagerID": None,
                "SearchOrderID": None,
                "cmbstatus": "Placed",
                "DatePlaced": None,
                "securitytype": None,
                "InstrumentCode": None,
                "Currency": None,
                "SearchEFMDealReference": None,
                "placementmethod": None,
                "BuyOrSell": None,
                "1authorise": "true",
                "1OrderID": parsedHTML.body.find("input", attrs={"id": "1OrderID"})["value"],
                "1InstrumentCurrency": parsedHTML.body.find("input", attrs={"name": f"{locatorIndex}InstrumentCurrency"})["value"],
                "1CustodianAccountID": parsedHTML.body.find("input", attrs={"id": f"{locatorIndex}CustodianAccountID"})["value"],
                "1ConfirmFilledQuantity": parsedHTML.body.find("input", attrs={"id": f"{locatorIndex}ConfirmFilledQuantity"})["value"],
                "1ConfirmFilledPrice": parsedHTML.body.find("input", attrs={"id": f"{locatorIndex}ConfirmFilledPrice"})["value"],
                "1ConfirmFilledValueExComm": parsedHTML.body.find("input", attrs={"id": f"{locatorIndex}ConfirmFilledValueExComm"})["value"],
                "1ConfirmDatePriced": parsedHTML.body.find("input", attrs={"id": f"{locatorIndex}ConfirmDatePriced"})["value"],
                "1ConfirmSettlementDate": parsedHTML.body.find("input", attrs={"id": f"{locatorIndex}ConfirmSettlementDate"})["value"],
                "1ConfirmFXRate": parsedHTML.body.find("input", attrs={"id": f"{locatorIndex}ConfirmFXRate"})["value"],
                "1ConfirmFee_EFMDilutionLevy": parsedHTML.body.find("input", attrs={"id": f"{locatorIndex}ConfirmFee_EFMDilutionLevy"})["value"],
                "1ConfirmFee_EFMInitialCharge": parsedHTML.body.find("input", attrs={"id": f"{locatorIndex}ConfirmFee_EFMInitialCharge"})["value"],
                "1ConfirmUT_InitialCharge": parsedHTML.body.find("input", attrs={"id": f"{locatorIndex}ConfirmUT_InitialCharge"})["value"],
                "1ConfirmUT_Discount": parsedHTML.body.find("input", attrs={"id": f"{locatorIndex}ConfirmUT_Discount"})["value"],
                "1EFMDealReference": parsedHTML.body.find("input", attrs={"id": f"{locatorIndex}EFMDealReference"})["value"]}
        return data

    def _getDataPooledCompletionForConfirmSAVE(self, htmlText):
        parsedHTML = BeautifulSoup(htmlText, features="html.parser")
        data = {"actiontype": "confirmsave",
                "webauditlogid": self.backOfficeRequests.webAuditLogId,
                "priceDate": None,
                "SearchFundManagerID": None,
                "SearchOrderID": None,
                "cmbstatus": "Placed",
                "DatePlaced": None,
                "securitytype": None,
                "InstrumentCode": None,
                "Currency": None,
                "SearchEFMDealReference": None,
                "placementmethod": None,
                "BuyOrSell": None,
                "1OrderID": parsedHTML.body.find("input", attrs={"name": "1OrderID"})["value"],
                "1CustodianAccountID": parsedHTML.body.find("input", attrs={"name": "1CustodianAccountID"})["value"],
                "1FilledQuantity": parsedHTML.body.find("input", attrs={"name": "1FilledQuantity"})["value"],
                "1FilledPrice": parsedHTML.body.find("input", attrs={"name": "1FilledPrice"})["value"],
                "1FilledValueExComm": parsedHTML.body.find("input", attrs={"name": "1FilledValueExComm"})["value"],
                "1Fee_EFMDilutionLevy": parsedHTML.body.find("input", attrs={"name": "1Fee_EFMDilutionLevy"})["value"],
                "1Fee_EFMInitialCharge": parsedHTML.body.find("input", attrs={"name": "1Fee_EFMInitialCharge"})["value"],
                "1DatePriced": parsedHTML.body.find("input", attrs={"name": "1DatePriced"})["value"],
                "1SettlementDate": parsedHTML.body.find("input", attrs={"name": "1SettlementDate"})["value"],
                "1UT_InitialCharge": parsedHTML.body.find("input", attrs={"name": "1UT_InitialCharge"})["value"],
                "1UT_Discount": parsedHTML.body.find("input", attrs={"name": "1UT_Discount"})["value"],
                "1DealReference": parsedHTML.body.find("input", attrs={"name": "1DealReference"})["value"],
                "1FXReverse": parsedHTML.body.find("input", attrs={"name": "1FXReverse"})["value"],
                "1FXRate": parsedHTML.body.find("input", attrs={"name": "1FXRate"})["value"]}
        return data

    def _getCashUploadData(self, accountNumber, amount):
        data = {"actiontype": "Cheques",
                "cashDesc1": None,
                "cashAmount1": None,
                "tbldebCred1": "CR",
                "cashAccount1": "Wrap",
                "txtCashAccount1": None,
                "tblbank1": "HSBC",
                "cashDesc2": None,
                "cashAmount2": None,
                "tbldebCred2": "CR",
                "cashAccount2": "Wrap",
                "txtCashAccount2": None,
                "tblbank2": "HSBC",
                "cashDesc3": None,
                "cashAmount3": None,
                "tbldebCred3": "CR",
                "cashAccount3": "Wrap",
                "txtCashAccount3": None,
                "tblbank3": "HSBC",
                "cashDesc4": None,
                "cashAmount4": None,
                "tbldebCred4": "CR",
                "cashAccount4": "Wrap",
                "txtCashAccount4": None,
                "tblbank4": "HSBC",
                "cashDesc5": None,
                "cashAmount5": None,
                "tbldebCred5": "CR",
                "cashAccount5": "Wrap",
                "txtCashAccount5": None,
                "tblbank5": "HSBC",
                "cashDesc6": None,
                "cashAmount6": None,
                "tbldebCred6": "CR",
                "cashAccount6": "Wrap",
                "txtCashAccount6": None,
                "tblbank6": "HSBC",
                "cashDesc7": None,
                "cashAmount7": None,
                "tbldebCred7": "CR",
                "cashAccount7": "Wrap",
                "txtCashAccount7": None,
                "tblbank7": "HSBC",
                "cashDesc8": None,
                "cashAmount8": None,
                "tbldebCred8": "CR",
                "cashAccount8": "Wrap",
                "txtCashAccount8": None,
                "tblbank8": "HSBC",
                "chequeDesc1": accountNumber,
                "chequeAmount1": amount,
                "chequeAccount1": accountNumber,
                "chequeDesc2": accountNumber,
                "chequeAmount2": amount,
                "chequeAccount2": accountNumber,
                "chequeDesc3": None,
                "chequeAmount3": None,
                "chequeAccount3": None,
                "chequeDesc4": None,
                "chequeAmount4": None,
                "chequeAccount4": None,
                "chequeDesc5": None,
                "chequeAmount5": None,
                "chequeAccount5": None,
                "chequeDesc6": None,
                "chequeAmount6": None,
                "chequeAccount6": None,
                "chequeDesc7": None,
                "chequeAmount7": None,
                "chequeAccount7": None,
                "chequeDesc8": None,
                "chequeAmount8": None,
                "chequeAccount8": None
                }
        return data

    def confirmOrder(self, htmlText):
        parsedHTML = BeautifulSoup(htmlText, features="html.parser")
        alertElement = parsedHTML.body.find("td", attrs={"class": "Alert"})
        if alertElement:
            PrintMessage(f"BO > Notification message: '{alertElement.text}'", inStepMessage=True)
            return True
        PrintMessage("BO > Notification message: 'it did not work - to check'", inStepMessage=True)
        return False

    @retry(exceptions=APIException, delay=5, tries=10)
    def waitForOrderStatusChangeTo(self, batchId, orderId, expectedState: OrderEnum):
        orderStatus = self._getMatchingBOOrder(batchId, orderId).status
        if orderStatus != expectedState.value:
            raise APIException(f"Expected order status to be: '{expectedState.value}' got: '{orderStatus}'")
        return orderStatus

    @retry(exceptions=APIException, delay=30, tries=5)
    def placeBatchAndWait(self, batchId):
        expectedStatus = OrderEnum.PLACED.value
        PrintMessage(f"BO > Waiting for batch: '{batchId}' to be with '{expectedStatus}' status", inStepMessage=True)
        htmlText = self.backOfficeRequests.postPrePooledDeals(False, autoplacebatchids=batchId)
        parsedHTML = BeautifulSoup(htmlText, features="html.parser")
        allElements = parsedHTML.body.find_all("td", attrs={"class": "TableData LAlign"})
        if not allElements:
            PrintMessage("No order records found", inStepMessage=True)

        for element in allElements:
            if expectedStatus in str(element):
                PrintMessage(f"Done: batch: '{batchId}' is '{expectedStatus}'", inStepMessage=True)
                return
        raise APIException()

    def _getMatchingBOOrder(self, batchId, orderId) -> WrapOrder:
        wrapOrders = self.backOfficeRequests.getWrapOrders(SearchBatchID=batchId)
        return wrapOrders.getWrapOrder(orderId)

    def getPooledCompletion(self, batchId):
        # Pooled Completions - 'navigating' to Pooled completions
        rawRespone = self.backOfficeRequests.getPooledCompletion(batchId)
        return self._getDataTestFill(rawRespone.text, batchId)

    def savePooledCompletion(self, testDataFill1, batchId):
        # Set date - semi save
        orderId = testDataFill1["1OrderID"]
        priceDate = testDataFill1["priceDate"]
        PrintMessage(f"BO > post pooled TEST SAVE completion, orderId: '{orderId}', priceDate: '{priceDate}'.", inStepMessage=True)
        rawResponse = self.backOfficeRequests.postPooledCompletion(testDataFill1)

        # Pooled Completions - proper save data
        PrintMessage("BO > post pooled SAVE completion.", inStepMessage=True)
        testDataFill2 = self._getDataFillSave(rawResponse.text, batchId)
        rawResponse = self.backOfficeRequests.postPooledCompletion(testDataFill2)

    def authorisePooledCompletion(self, batchId, priceDate):
        # Authorise Pooled Completions
        currentPooledCompletions = self.backOfficeRequests.authorisePooledCompletions("GET")

        # SAVE
        PrintMessage("BO > Authorise pooled completion.", inStepMessage=True)

        preFinalDataFill = self._getDataPooledCompletionForSAVE(currentPooledCompletions, batchId)
        preFinalDataFill["priceDate"] = priceDate
        saveActionResponse = self.backOfficeRequests.authorisePooledCompletions("POST", data=preFinalDataFill)

        # CONFIRM SAVE
        PrintMessage("BO > Confirm SAVE pooled completion.", inStepMessage=True)
        confirmSaveActionResponse = self._getDataPooledCompletionForConfirmSAVE(saveActionResponse)
        confirmSaveActionResponse["priceDate"] = priceDate
        completedOrderResponse = self.backOfficeRequests.authorisePooledCompletions("POST", data=confirmSaveActionResponse)

        if not self.confirmOrder(completedOrderResponse):
            raise APIException(f"Failed authorise Pooled completion for batch order:'{batchId}'.")

    @retry(exceptions=(APIException, TypeError), delay=30, tries=5)
    def processWrapOrder(self, wrapOrder):
        PrintMessage(f"BO > wrap-order: '{wrapOrder.batchOrderId}' status: '{wrapOrder.status}'", inStepMessage=True)
        priceDate = datetime.now().strftime("%d-%b-%Y")
        batchId, orderId = wrapOrder.batchOrderId.split(".")  # split S.B.O

        orderStatus = self._getMatchingBOOrder(batchId, orderId).status

        if orderStatus in [OrderEnum.AUTHORISED_SWITCH.value]:
            raise APIException(f"BO > Order ({wrapOrder.batchOrderId}) not ready for BO action: '{orderStatus}' - Wait.")

        if orderStatus in [OrderEnum.AUTHORISED.value]:
            raise APIException(f"BO > Order ({wrapOrder.batchOrderId}) not YET ready for BO action: '{orderStatus}' - Wait.")

        PrintMessage(f"BO > make attempt to set order: '{orderStatus}' as completed for batch: '{batchId}'.", inStepMessage=True)

        if orderStatus == OrderEnum.PRE_POOLED.value:
            self.backOfficeRequests.postPrePooledDeals(autoplacebatchids=batchId)
            orderStatus = self._getMatchingBOOrder(batchId, orderId).status

        if orderStatus == OrderEnum.POOLED.value:
            # Pre-Pooled Deals - SAVE
            self.placeBatchAndWait(batchId)
            orderStatus = self.waitForOrderStatusChangeTo(batchId, orderId, OrderEnum.PLACED)

        if orderStatus == OrderEnum.PLACED.value:
            try:
                testDataFill1 = self.getPooledCompletion(batchId)
                self.savePooledCompletion(testDataFill1, batchId)
                orderStatus = self._getMatchingBOOrder(batchId, orderId).status
            except TypeError:
                # Order might be at the next stage. There seem no way to distinguish it though. Both are status: PLACED
                pass

        if orderStatus == OrderEnum.PLACED.value:
            self.authorisePooledCompletion(batchId, priceDate)

    @retry(exceptions=APIException, delay=30, tries=8)
    def setDealToComplete(self, batchId, platformOrders):
        """
        Implements Test Case 1402107: Servicing - Mutual Funds deal completion on BackOffice
        """
        platformOrders = [platformOrders] if not isinstance(platformOrders, list) else platformOrders

        try:
            wrapOrders = self.backOfficeRequests.getWrapOrders(SearchBatchID=batchId)
            self.backOfficeRequests.getPooledDeals()  # to refresh webAuditLogId

            for wrapOrder in wrapOrders.iterateOrdered():
                batchId, orderId = wrapOrder.batchOrderId.split(".")  # split S.B.O
                if orderId not in str(platformOrders):
                    continue

                self.processWrapOrder(wrapOrder)

        except Exception as e:
            tb = traceback.format_exc()
            PrintMessage(f"Encountered exception {type(e)}, with args {e.args}")
            PrintMessage(str(e))
            PrintMessage(f"traceback: {tb}")
            raise APIException(str(e)) from e

    def closeAllOrders(self, openOrderBatches):
        """
        Check if there are any open deals for given account via UI
        Make an attempt to close those via API
        Closing via API might fail due to UI and API being out of sync, in such case retry until certain
        """
        for batchNumber, orders in openOrderBatches.items():
            PrintMessage(f"PlatformRequestHelper > Closing order on batch number '{batchNumber}'", inStepMessage=True)
            self.setDealToComplete(batchNumber, orders)

    def uploadCash(self, accountNumber, amount):
        try:
            PrintMessage(f"BO > Upload cheque cash for the provided WP: {accountNumber}", inStepMessage=True)
            cashTestDataFill = self._getCashUploadData(accountNumber, amount)
            htmlText = self.backOfficeRequests.uploadChequeCash(cashTestDataFill)
            parsedHTML = BeautifulSoup(htmlText, features="html.parser")
            successCashUploadMessage = parsedHTML.body.find("td", attrs={"class": "Alert"}).text.strip()

            if not successCashUploadMessage:
                raise APIException("Cash upload for cheques failed")
            PrintMessage("Validated the cash upload for cheque is done successfully", inStepMessage=True)

        except Exception as e:
            tb = traceback.format_exc()
            PrintMessage(f"Encountered exception {type(e)}, with args {e.args}")
            PrintMessage(str(e))
            PrintMessage(f"traceback: {tb}")
            raise APIException(str(e)) from e
