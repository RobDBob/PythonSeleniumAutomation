

def getValueForKeyCaseInsensitive(data: dict, key: str, defaultValue=None) -> str:
    if data is None:
        return defaultValue

    actualValue = None
    for k, v in data.items():
        if k.lower() == key.lower():
            if v is None:
                return defaultValue
            return v

    if defaultValue is not None and isinstance(actualValue, type(defaultValue)):
        return actualValue

    if actualValue is None:
        return defaultValue

    return defaultValue


def addToListSkipDuplicates(mainList: list, incomingList: list):
    for incomingItem in incomingList:
        if incomingItem not in mainList:
            mainList.append(incomingItem)
