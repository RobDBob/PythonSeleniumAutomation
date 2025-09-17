import requests


def cleanUpRawResponseText(rawResponseText):
    """
    Remove /n /r /t from response
    """
    return ''.join(s for s in rawResponseText if ord(s) > 31 and ord(s) < 126)


def isResponseJSON(response):
    try:
        response.json()
        return True
    except requests.exceptions.JSONDecodeError:
        return False


def paramsToURL(params):
    paramList = [f"{k}={params[k]}" for k in params]
    return "&".join(paramList)
