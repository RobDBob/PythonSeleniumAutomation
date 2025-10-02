from bs4 import BeautifulSoup
from CommonCode.API.BackOffice.BOEnums import OrderEnum

# pylint: disable= too-many-instance-attributes, unnecessary-dunder-call

ACTION_ORDER = (OrderEnum.PRE_POOLED.value,
                OrderEnum.POOLED.value,
                OrderEnum.PLACED.value,
                OrderEnum.AUTHORISED.value,
                OrderEnum.AUTHORISED_SWITCH.value,
                OrderEnum.PROCESSING.value,
                OrderEnum.COMPLETED.value)


class WrapOrder:
    def __init__(self, dataRow: list):
        # big assume, that comes-in sorted
        self.batchOrderId = dataRow[0]
        self.account = dataRow[1]
        self.batch = dataRow[2]
        self.order = dataRow[3]
        self.orderType = dataRow[4]
        self.orderQty = dataRow[5]
        self.orderValue = dataRow[6]
        self.status = dataRow[7].strip() if dataRow[7] else dataRow[7]
        self.dateCreated = dataRow[8]


class WrapOrdersData(list):
    def __init__(self, requestResponseText):
        super().__init__()
        self._populateData(requestResponseText)

    def _populateData(self, aspxText):
        parsedHTML = BeautifulSoup(aspxText, features="html.parser")
        tableElement = parsedHTML.body.find("table", attrs={"class": "Table"})
        # skip first and last row
        for dataRow in tableElement.findChildren("tr")[1:-1]:
            self.append(WrapOrder([k.text for k in dataRow.findChildren("td")]))

    def getWrapOrder(self, orderId):
        for item in self.__iter__():
            if orderId in item.batchOrderId:
                return item
        return None

    def iterateOrdered(self):
        local = list(self.__iter__())
        return sorted(local, key=lambda item: ACTION_ORDER.index(item.status))
