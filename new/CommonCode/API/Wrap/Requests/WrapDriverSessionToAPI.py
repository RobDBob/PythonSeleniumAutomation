from CommonCode.API import APIConstants


class WrapDriverSessionToAPI:
    _headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/json; charset=UTF-8",
        "Cookie": None,
        "Referer": None,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "anti-forgery-token": None}

    def __init__(self, apiCookiesData: dict):
        self._removeUnwantedCookies(apiCookiesData)
        self._setAntiForgeryHeader(apiCookiesData)
        self._setCookieHeader(apiCookiesData)

    def _removeUnwantedCookies(self, apiCookiesData):
        for cookie in apiCookiesData:
            if "sameSite" in cookie:
                cookie.pop("sameSite")
            if "httpOnly" in cookie:
                value = cookie.pop("httpOnly")
                cookie["rest"] = {"HttpOnly": value}

    def _setAntiForgeryHeader(self, apiCookiesData):
        for cookie in apiCookiesData:
            if cookie["name"] == APIConstants.ANTIFORGERY_COOKIE_NAME:
                self._headers[APIConstants.REQUEST_HEADER_ANTIFORGERY] = cookie["value"]
                break

    def _setCookieHeader(self, apiCookiesData):
        cookies = [f"{k['name']}={k['value']}" for k in apiCookiesData]
        self._headers[APIConstants.REQUEST_HEADER_COOKIE] = "; ".join(cookies)

    @property
    def headers(self):
        return self._headers
