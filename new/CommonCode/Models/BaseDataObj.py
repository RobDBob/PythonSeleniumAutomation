class BaseDataObj:
    def __init__(self, data):
        self._data = data

    @property
    def dataDict(self) -> dict:
        """
        Might be a list or dict, depends on subclass
        """
        return self._data

    @property
    def dataList(self) -> list:
        """
        Might be a list or dict, depends on subclass
        """
        return self._data
