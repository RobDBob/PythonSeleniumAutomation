import logging
import sys
import requests
from bs4 import BeautifulSoup
from retry import retry
from CommonCode.API.APIHelper import cleanUpRawResponseText
from CommonCode.CustomExceptions import APIException
from CommonCode.TestExecute.Logging import PrintMessage


class PlatformRequestsUserFirstLogin:
    REQUEST_HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        # "Host": slwrapte5.fnz.co.uk,
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "sec-ch-ua": "'Google Chrome';v='135', 'Not-A.Brand';v='8', 'Chromium';v='135'",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
    }

    def __init__(self, baseUrl: str):
        self.baseUrl = baseUrl
        self.session = requests.Session()
        self.session.headers = PlatformRequestsUserFirstLogin.REQUEST_HEADERS

    @retry(APIException, tries=2)
    def executeRequest(self, method, url, **kwargs):
        """
        Generic method for request execution
        method: GET/PUT etc
        """
        try:
            response = self.session.request(method, url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            PrintMessage(f"Connection error: {e}", level=logging.ERROR)
            raise APIException("Connection error - request failed") from e

        if "AccessDenied" in response.text:
            PrintMessage(response.history, level=logging.DEBUG)
            sys.exit(1)

        PrintMessage(f"Platform Requests > '{method}:{response.url}'", level=logging.DEBUG)
        return response

    def firstUserLoginAndPasswordUpdate(self, userName, userPassword, newPassword):
        """
        Method to be used for first time user login
        User is expected to be prompted with password change request
        """
        PrintMessage(f"Platform Requests > updating user: '{userName}' with new password")

        # get fnz home
        self.executeRequest("GET", f"{self.baseUrl}/fnzhome.aspx")

        # attempt to login
        getLoginResponse = self.executeRequest("POST", f"{self.baseUrl}/fnzhome.aspx", data={"txtusername": userName, "txtpassword": userPassword})
        if "Invalid username or password entered." in getLoginResponse.text:
            PrintMessage("wrong password provided: '{userPassword}'")
            sys.exit(1)

        # GET terms and conditions
        getTermsAndConditionsResponse = self.executeRequest("GET", f"{self.baseUrl}/admin/termsandconditions/termsandconditions.aspx")

        # POST terms and conditions
        parsedHTML = BeautifulSoup(cleanUpRawResponseText(getTermsAndConditionsResponse.text), features="html.parser")
        accemptTermsAndConditionsData = {"__RequestVerificationToken": parsedHTML.body.find("input", attrs={"id": "__RequestVerificationToken"})["value"],
                                         "RandomString": parsedHTML.body.find("input", attrs={"id": "RandomString"})["value"],
                                         "termsAndConditionsAccepted": "on",
                                         "actiontype": "Accepted",
                                         "version": 4}

        self.executeRequest("POST", f"{self.baseUrl}/admin/termsandconditions/termsandconditions.aspx", data=accemptTermsAndConditionsData)

        # GET customer
        self.executeRequest("GET", f"{self.baseUrl}/wpadviser/en-gb/dashboard/home/main/customer")

        # GET password change
        getPasswordChangeResponse = self.executeRequest("GET", f"{self.baseUrl}/admin/logindetails/logindetails-changepassword.aspx")

        # POST password change
        parsedHTML = BeautifulSoup(cleanUpRawResponseText(getPasswordChangeResponse.text), features="html.parser")
        updatePasswordData = {"__RequestVerificationToken": parsedHTML.body.find("input", attrs={"id": "__RequestVerificationToken"})["value"],
                              "RandomString": parsedHTML.body.find("input", attrs={"id": "RandomString"})["value"],
                              "actiontype": "go",
                              "currentpassword": userPassword,
                              "newpassword": newPassword,
                              "confirmpassword": newPassword}
        postChangePasswordResponse = self.executeRequest("POST", f"{self.baseUrl}/admin/logindetails/logindetails-changepassword.aspx", data=updatePasswordData)

        if "Your password has been successfully changed." in postChangePasswordResponse.text:
            PrintMessage(f"Password for user: '{userName}' updated succesfully")
        else:
            PrintMessage("Password WAS NOT updated succesfully for user '{userName}'")
