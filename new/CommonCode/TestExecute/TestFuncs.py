def flattentTestsSuitesIntoGen(testSuiteOrCase):
    """Iterate through all of the test cases in 'testSuiteOrCase'."""
    try:
        suite = iter(testSuiteOrCase)
    except TypeError:
        yield testSuiteOrCase
    else:
        for test in suite:
            yield from flattentTestsSuitesIntoGen(test)


def getAllValuesForKey(incDict: dict, keyName: str):
    values = []
    for k, v in incDict.items():
        if isinstance(v, dict):
            values.extend(getAllValuesForKey(v, keyName))
        if keyName in k:
            values.append(v)
    return values
