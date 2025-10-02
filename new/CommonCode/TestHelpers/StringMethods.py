import html
import locale
import random
import string
from faker import Faker
from CommonCode.TestExecute.Logging import PrintMessage


def getRandomNINString(length=5):
    """
    Used for generating NIN numbers which needs to have specific alphabet/range as prefix and postfix
    The characters D, F, I, Q, U, O and V are not Preferred
    Prefixes BG, GB, KN, NK, NT, TN and ZZ are not to be used
    Postfix only A, B, C and D are preferred
    """
    firstBlockStr = ''.join((random.choice('acehjlmxyprsw') for i in range(length)))
    lastBlockString = ''.join((random.choice('abcd') for i in range(length)))
    return firstBlockStr.upper(), lastBlockString.upper()


def getUniqueAlphaNumericString(prefix='random'):
    """
    Used for any name that needs to be unique and can contains Letter (lower and upper case) and Digits
    :param prefix:
    :return:
    """
    chars = string.ascii_letters + string.digits
    randomText = ''.join([random.choice(chars) for _ in range(5)])

    return prefix + randomText


def getUniqueAlphaString(prefix='random', length=5):
    """
    Used for any name that needs to be unique and can contains Letter (lower and upper case) and Digits
    :param prefix:
    :return:
    """
    chars = string.ascii_letters
    randomText = ''.join([random.choice(chars) for _ in range(length)])

    return prefix + randomText


def getUniqueName(prefix='random'):
    """
    Used for Authentication names, as this unique name is only composed of Digits (Authentication names cannot
    contain Uppercase characters)
    :param prefix:
    :return:
    """
    chars = string.digits
    randomText = ''.join([random.choice(chars) for _ in range(5)])

    return prefix + randomText


def randomNumber(minValue, maxValue, exceptValue=None):
    """
    Method  generates random number

    :param min_value:1
    :param max_value:65535
    :param except_value: either single value or a list of values. Value(s) to avoid when generating a number
    :return:
    """
    if exceptValue is None:
        exceptValue = []
    elif not isinstance(exceptValue, list):
        exceptValue = [exceptValue]

    random.seed()
    number = random.randrange(minValue, maxValue)

    if exceptValue and number in exceptValue:
        return randomNumber(minValue, maxValue, exceptValue)

    return number


def randomNumberAsString(minValue, maxValue, exceptValue=None):
    return str(randomNumber(minValue, maxValue, exceptValue))


def getFakeUKAddressAPI() -> dict:
    """
    New address is composed of 3-4 parts
    Country: 61 represents UK in api call
    """
    newAddress = Faker("en_GB").address().split('\n')
    postCodeIndex = newAddress.index(newAddress[-1])
    result = {"PostCode": newAddress.pop(postCodeIndex),
              "Country": 61}
    for i, address in enumerate(newAddress):
        result[f"Address{i+1}"] = address

    return result


def getFakeUKAddress() -> dict:
    """
    New address is composed of 3-4 parts
    Country: 61 represents UK in api call
    """
    newAddress = Faker("en_GB").address().split('\n')
    postCodeIndex = newAddress.index(newAddress[-1])
    result = {"PostCode": newAddress.pop(postCodeIndex)}
    for i, address in enumerate(newAddress):
        result[f"AddressLine{i+1}"] = address

    return result


def compareText(text1, text2, caseSensitive=True):
    """
    unescapes html characters back to readable string
    """
    text1Unescaped = html.unescape(text1)
    text2Unescaped = html.unescape(text2)
    if caseSensitive:
        return text1Unescaped == text2Unescaped
    return text1Unescaped.lower() == text2Unescaped.lower()


def formatNumberAsCurrency(value):
    return f'£{int(value):,.2f}'

# pylint: disable=W0622


def removeEmptyItemsFromList(list):
    return [string for string in list if string != ""]


def addItemToAnExistingDict(dictionary, key, value):
    dictionary[key] = value
    return dictionary


def roundDecimalValue(decimalValue, decimalPoints=2):
    return str(round(decimalValue, decimalPoints))


def calculatePercentageValue(totalValue, percentage):
    value = float((float(percentage) / 100) * totalValue)
    return f'£{float(value):,.2f}'


def getSubtractedCurrencyValue(value1, value2):
    """Expected tax relief Currency format value as £3,125.00 and a single payment input int format value as 2500.
    which needs to be subtracted and return again with Currency format as £625.00"""
    convertedValue1 = round(convertCurrencyInStringFormatToFloat(value1), 2)
    convertedValue2 = round(value2, 2)
    substractedValue = convertedValue1 - convertedValue2
    return f'£{float(substractedValue):,.2f}'


def getAddedCurrencyValue(value1, value2):
    """Expected tax relief Currency format value as £3,125.00 and a single payment input int format value as 2500.
    which needs to be added and return again with Currency format as £625.00"""
    convertedValue1 = round(convertCurrencyInStringFormatToFloat(value1), 2)
    convertedValue2 = round(value2, 2)
    addedValue = convertedValue1 + convertedValue2
    return f'£{float(addedValue):,.2f}'


def convertCurrencyInStringFormatToFloat(currencyString):
    return float(currencyString.replace('£', '').replace(',', ''))


def getNumberFromSortCode(sortCode):
    return str(sortCode.replace('-', ''))


def tryToInt(stringValue):
    try:
        return int(stringValue)
    except ValueError:
        PrintMessage(f"Failed to convert {stringValue} to int value!")
        return stringValue


def sortListOfDicts(listOfDicts, sortKey, reverse=False):
    """
    Sorts a list of dictionaries by a specified key.

    :param listOfDicts: List of dictionaries to be sorted.
    :param sortKey: The key in the dictionary to sort by.
    :param reverse: If True, sorts in descending order. Default is False (ascending order).
    :return: A new sorted list of dictionaries.
    """
    return sorted(listOfDicts, key=lambda x: x[sortKey], reverse=reverse)


def addThousandSeparators(numString):
    """
    Method to add thousand seperators , eg input numeric string 2000 will be returned as 2,000
    """
    try:
        return f"{int(numString):,}"
    except ValueError:
        PrintMessage(f"Invalid input, {numString} is not a numeric string")
        return numString


def reprAsCurrency(valueToConvert):
    locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')
    return locale.currency(valueToConvert, grouping=True, symbol=False)


def roundDecimalValueToFloat(decimalValue):
    return round(float(decimalValue), 2)


def calculateValueByPercentage(percentage, totalValue, roundOff=True):
    value = (float(totalValue) / 100) * percentage
    if roundOff:
        return round(float(value), 2)
    return int(float(value) * 100) / 100


def calculatePercentageByValue(actualValue, totalValue):
    value = float(actualValue) * 100 / float(totalValue)
    return round(value, 0)


def truncateFloatTo2Decimals(value):
    """
    Returns the float value truncated to 2 decimal places without rounding.
    """
    value = float(value)
    return int(value * 100) / 100
