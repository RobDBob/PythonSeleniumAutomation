from bs4 import BeautifulSoup


class UnderlyingOrder:
    def __init__(self, dataRow:list):
        # big assume, data comes-in pre-sorted
        self.account = dataRow[0].strip()
        self.orderId = dataRow[2].strip()
        self.batchId = dataRow[3].strip()
        self.dealSource = dataRow[4]
        self.dateCreated = dataRow[5]
        self.orderDescription = dataRow[6]


class PooledCompletionDetails(list):
    def __init__(self, requestResponseText):
        super().__init__()
        self._populateData(requestResponseText)
        self._populateUnderlyingData(requestResponseText)

    def _populateData(self, aspxText):
        parsedHTML = BeautifulSoup(aspxText, features="html.parser")

        # first table is one we are interested in
        tableElement = parsedHTML.body.find_all("table", attrs={"class":"table"})[0]

        # skip first two rows, only single row is expected to be present
        dataRow = tableElement.findChildren("tr")[2:][0]
        dataCells = dataRow.findChildren("td")

        self.account = dataCells[0].text
        self.orderId = dataCells[1].text.strip()
        self.dateCreated = dataCells[2].text
        self.managedFund = f"{dataCells[3].text} {dataCells[4].text}"
        self.orderDescription = dataCells[5].text.strip()
        self.drp = dataCells[6].text.strip()

    def _populateUnderlyingData(self, aspxText):
        parsedHTML = BeautifulSoup(aspxText, features="html.parser")

        # second table is one we are interested in
        tableElement = parsedHTML.body.find_all("table", attrs={"class":"table"})[1]
        
        # skip first two rows
        for dataRow in tableElement.findChildren("tr")[2:]:
            self.append(UnderlyingOrder([k.text for k in dataRow.findChildren("td")]))

    def isBatchIdOnUnderlyingOrders(self, batchId):
        for item in self.__iter__():
            if batchId in item.batchId:
                return True
        return False