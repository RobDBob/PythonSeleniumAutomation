from CommonCode.Models.BaseDataObj import BaseDataObj
from CommonCode.Models.ClientDataObj import ClientDataObj
from CommonCode.Models.ClientTypeObj import ClientTypeObj
from CommonCode.Models.ProductsDataObj import ProductsDataObj
from CommonCode.Models.WrapperDataObj import WrapperDataObj
from TestPages import DataEnums


class AccountDataObj(BaseDataObj):
    @property
    def clientDetails(self):
        return ClientDataObj(self._data.get(DataEnums.NEW_CLIENT_DETAILS, {}), self._data.get(DataEnums.FULL_CLIENT_DETAILS, {}))

    @property
    def clientTypeObj(self):
        return ClientTypeObj(self._data.get(DataEnums.NEW_CLIENT_TYPE, {}))

    @property
    def wrapperObj(self):
        return WrapperDataObj(self._data.get(DataEnums.WRAPPER_SELECTION, {}))

    @property
    def productsObj(self):
        return ProductsDataObj(self._data.get(DataEnums.PRODUCTS, {}))
