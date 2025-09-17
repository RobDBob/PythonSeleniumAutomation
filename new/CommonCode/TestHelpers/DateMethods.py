from datetime import datetime, timedelta


class NotAWeekendException(Exception):
    pass


def getMinuteRange(currentMinute, minuteRange=1):
    """
    cheatsheet:
    - https://docs.python.org/3/library/datetime.html
    - https://strftime.org/
    returns range from given minute, i.e. for minute at 55 the range in which it falls is 45-59 and 0-5
    """
    if currentMinute - minuteRange < 0:
        return list(range(60 - minuteRange, 60)) + list(range(0, minuteRange))
    if currentMinute + minuteRange > 60:
        return list(range(currentMinute - minuteRange, 60)) + list(range(0, 60 - currentMinute))
    return list(range(currentMinute - minuteRange, currentMinute + minuteRange))


def getFutureWeekdayFromTodayFormatted(minInFuture, avoid27thOnwards=True, outputFormat="%d/%m/%Y") -> str:
    return getFutureWeekdayFromToday(minInFuture, avoid27thOnwards).strftime(outputFormat)


def getFutureWeekdayFromToday(numberOfWorkingDays, avoid27thOnwards=True) -> datetime:
    """
    It will return the future Weekday after a certain number of Weekdays and also avoid dates after 27th of each month.
    """
    today = datetime.now().date()
    workDays = 0
    futureDate = today
    while workDays < numberOfWorkingDays:
        futureDate += timedelta(days=1)
        if futureDate.weekday() < 5:
            workDays += 1
    if avoid27thOnwards:
        while futureDate.weekday() > 4 or futureDate.day > 27:
            futureDate += timedelta(days=1)
    return futureDate


def addDaysToDate(inputDateString, daysToAdd, dateFormat="%d/%m/%Y"):
    """
    If the resulting date is beyond 28th then it selects 1st day of the next month.
    For December month it increments to next year(i.e 1st Jan)
    As regular payment cannot be placed on these dates (29th , 30th and 31st)
    """
    inputDate = datetime.strptime(inputDateString, dateFormat)
    newDate = inputDate + timedelta(days=daysToAdd)
    if newDate.day > 28:
        newDate = newDate.replace(day=1)
        newMonth = newDate.month + 1 if newDate.month < 12 else 1
        newYear = newDate.year + 1 if newDate.month == 12 else newDate.year
        newDate = newDate.replace(month=newMonth, year=newYear)
    newDateString = newDate.strftime(dateFormat)
    return newDateString


def addWeekdaysToDate(inputDateString, daysToAdd, dateFormat="%d/%m/%Y"):
    """
    Adds 'daysToAdd' weekdays to today's date, excluding weekends.
    """
    inputDate = datetime.strptime(inputDateString, dateFormat)
    futureDate = inputDate
    addedDays = 0

    while addedDays < daysToAdd:
        futureDate += timedelta(days=1)
        if futureDate.weekday() < 5:  # Monday to Friday are 0-4
            addedDays += 1

    # Adjust the date if it falls beyond the 28th
    if futureDate.day > 28:
        futureDate = futureDate.replace(day=1)
        newMonth = futureDate.month + 1 if futureDate.month < 12 else 1
        newYear = futureDate.year + 1 if futureDate.month == 12 else futureDate.year
        futureDate = futureDate.replace(month=newMonth, year=newYear)

    futureDateString = futureDate.strftime("%d/%m/%Y")
    return futureDateString


def getTodaysDate(dateFormat="%d/%m/%Y"):
    return (datetime.now().date()).strftime(dateFormat)


def formateStringDateToCompare(dateString, dateFormatIn, dateFormatRequired):
    date = datetime.strptime(dateString, dateFormatIn)
    return date.strftime(dateFormatRequired)


def getTimeStamp():
    """
    returns HourMinuteSecond-Microsecond:
    :return: str: '102029-992192'
    """
    return datetime.now().strftime("%H%M%S-%f")


def verifyTimeStampWithinRange(initialTimeStamp, timeStampToCheck, finalTimeStamp, dateFormat):
    formattedInitalTimeStamp = initialTimeStamp.strftime(dateFormat)
    formattedTimeStampToCheck = timeStampToCheck.strftime(dateFormat)
    formattedFinalTimeStamp = finalTimeStamp.strftime(dateFormat)
    return formattedInitalTimeStamp <= formattedTimeStampToCheck <= formattedFinalTimeStamp


def verifyDateTimeObjectFormatWithinRange(initialTimeStamp, timeStampToCheck, finalTimeStamp):
    return initialTimeStamp <= timeStampToCheck <= finalTimeStamp


def parseSafelyToDateTime(textValue, dateFormat):
    try:
        return datetime.strptime(textValue, dateFormat)
    except (TypeError, ValueError):
        return None


def getCurrentDateTimeWithoutSeconds():
    return datetime.now().replace(microsecond=0).replace(second=0)


def generateRequiredDateOfBirth(years, months):
    """
    Generate a date of birth based on the given years and months offset from today.

    Args:
        years (int): Number of years to subtract from today's date.
        months (int): Number of months to subtract from today's date.

    Returns:
        str: Date of birth in the format 'DD/MM/YYYY'.
    """
    today = datetime.today()
    targetYear = today.year - years
    targetMonth = today.month - months

    if targetMonth <= 0:
        targetYear -= 1
        targetMonth += 12

    try:
        dob = today.replace(year=targetYear, month=targetMonth)
    except ValueError:
        dob = today.replace(year=targetYear, month=targetMonth, day=1) - timedelta(days=1)

    return dob.strftime("%d/%m/%Y")
