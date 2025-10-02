from CommonCode.Models.BaseDataObj import BaseDataObj
from CommonCode.Models.ProductDataObj import ProductDataObj
from TestPages import DataEnums


class ProductsDataObj(BaseDataObj):
    def getProductData(self, productName):
        matchedProducts = [k for k in self.dataList if k[DataEnums.PRODUCT_TYPE] == productName]
        return ProductDataObj(matchedProducts[0])
