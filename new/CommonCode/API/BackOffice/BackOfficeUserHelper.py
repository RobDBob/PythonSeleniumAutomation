import re
import sys
from io import StringIO
import requests
from bs4 import BeautifulSoup
from lxml import etree
from CommonCode.API.APIHelper import cleanUpRawResponseText
from CommonCode.API.BackOffice.BackOfficeRequests import BackOfficeRequests
from CommonCode.API.Objects.BOUser import BOUserObj
from CommonCode.API.RequestHelpers import extractURLParameters
from CommonCode.TestExecute.Logging import PrintMessage

# pylint: disable = I1101:c-extension-no-member


class BackOfficeUserHelper:
    """
    This class is used to manage back office users.
    """
    NO_USER_FOUND_MESSAGE = "No users were found matching the specified criteria."
    USER_PERMISSIONS_COPIED_MESSAGE = "User website and client account access permissions have been successfully duplicated."
    PASSWORD_CHANGED_MESSAGE = "Your password has been successfully changed."
    INVALID_USER_PASSWORD_MESSAGE = "Invalid username or password entered."

    def __init__(self, backOfficeUrl: str, userName: str, userPassword: str):
        self.backOfficeUrl = backOfficeUrl
        self.sessionUserName = userName
        self.backOfficeRequests = BackOfficeRequests(self.backOfficeUrl, userName, userPassword)

    def verificationToken(self):
        """
        Back office helper class : BO Request Method Call to get the request verification token
        """
        responseText = self.backOfficeRequests.maintenanceTabMaintainUserRequest(method="GET")
        parsedHTML = BeautifulSoup(responseText, features="html.parser")
        verificationToken = parsedHTML.body.find("input", attrs={"id": "__RequestVerificationToken"})["value"]
        randomString = parsedHTML.body.find("input", attrs={"id": "RandomString"})["value"]
        return verificationToken, randomString

    def _getFindUserDataTestFill(self, verificationToken, randomString, userlogon):
        return {"__RequestVerificationToken": verificationToken,
                "RandomString": randomString,
                "actiontype": "search",
                "popup": 0,
                "formobj": None,
                "clientidobj": None,
                "clientinfoobj": None,
                "searchfirstname": None,
                "searchlastname": None,
                "userlogon": userlogon,
                "email": None,
                "searchuserid": None,
                "searchcompany": None,
                "searchadvcode": None,
                "searchStatus": "Enabled",
                "userType": "Staff"}

    def getSaveUserDataFill(self, verificationToken, randomString, boUser: BOUserObj):
        """
        lock password: "ostlocksignature": "on",
        unlock password: "ostunlocksignature": "on",
        """
        return {"__RequestVerificationToken": verificationToken,
                "RandomString": randomString,
                "actiontype": "savenew",
                "type": None,
                "searchuserid": boUser.userId,
                "prevhelplogassignee": 0,
                "title": None,
                "firstname": boUser.firstname,
                "initial": None,
                "surname": boUser.surname,
                "salutation": None,
                "email": boUser.email,
                "address1": None,
                "city": None,
                "address2": None,
                "postcode": None,
                "address3": None,
                "country": boUser.country,
                "workphone": None,
                "homephone": None,
                "mobile": None,
                "fax": None,
                "otherphones": None,
                "company": boUser.company,
                "organisationname": None,
                "organisationid": None,
                "workstream": 0,
                "department": None,
                "position": None,
                "clienttype": boUser.clienttype,
                "owner": boUser.owner,
                "notes1": None,
                "notes2": None,
                "webname": boUser.webname,
                "password": boUser.password,
                "confirmpassword": boUser.confirmPassword}

    def getBOUserByUserLogon(self, userLogon) -> BOUserObj:
        """
        Back office helper class : BO Request Method Call to get the User Type and Status
        """
        htmlParser = etree.HTMLParser()

        testDataFill = self._getFindUserDataTestFill(*self.verificationToken(), userlogon=userLogon)
        findUserResponseText = self.backOfficeRequests.maintenanceTabFindUsersRequest(testDataFill)

        if self.NO_USER_FOUND_MESSAGE in findUserResponseText:
            PrintMessage(f"User '{userLogon}' not found in Back Office", inStepMessage=True)
            return None

        findUserResponseTree: etree.ElementBase = etree.parse(StringIO(findUserResponseText), htmlParser)

        boUserEditQueryString = findUserResponseTree.find(".//td[@id='username0']//a").get("href")
        urlParameters = extractURLParameters(boUserEditQueryString)
        userEdidDataText = self.backOfficeRequests.maintenanceTabMaintainUserRequest(method="GET", params=urlParameters)
        userEdidDataTree: etree.ElementBase = etree.parse(StringIO(userEdidDataText), htmlParser)
        userEditTableElement = userEdidDataTree.find(".//table[@class='Panel']")

        boUserSiteAccessQueryString = findUserResponseTree.find(".//td[@id='usersiteaccess0']//a").get("href")
        urlParameters = extractURLParameters(boUserSiteAccessQueryString)
        userSiteAccessDataText = self.backOfficeRequests.maintenanceTabUserSiteAccessRequest(method="GET", params=urlParameters)
        userSiteAccessDataTree: etree.ElementBase = etree.parse(StringIO(userSiteAccessDataText), htmlParser)
        userSiteAccessTableElement = userSiteAccessDataTree.find(".//table[@class='Panel']")

        boUser = BOUserObj()
        boUser.updateFromResponses(userEditTableElement, userSiteAccessTableElement)
        return boUser

    def unlockUserPassword(self, userLogon):
        """
        Back office helper class : BO Request Method Call to unlock the User
        userLogon: i.e: test368_wst
        """
        boUser: BOUserObj = self.getBOUserByUserLogon(userLogon)
        # Equivalent to: In Maintenance tab > Find User > Click Search

        if not boUser:
            PrintMessage(f"User '{userLogon}' not found in Back Office. Exit.", inStepMessage=True)
            return
        if not boUser.userPasswordLocked:
            PrintMessage(f"User '{userLogon}' is not password locked. Exit.", inStepMessage=True)
            return
        PrintMessage(f"User '{userLogon}' is password locked. Making attempt to unlock.", inStepMessage=True)

        editExistinUserParameters = {
            "type": "EDIT",
            "actiontype": "savenew",
            "searchuserid": boUser.userId
        }
        editExistingUserPayload = self.getSaveUserDataFill(*self.verificationToken(), boUser=boUser)
        editExistingUserPayload["ostunlocksignature"] = "on"
        editExistingUserPayload["type"] = "EDIT"
        self.backOfficeRequests.maintenanceTabMaintainUserRequest(method="POST", params=editExistinUserParameters, data=editExistingUserPayload)

        boUser: BOUserObj = self.getBOUserByUserLogon(userLogon)
        if boUser.userPasswordLocked:
            PrintMessage(f"Failed to unlock password for user: '{userLogon}'", inStepMessage=True)
            return
        PrintMessage(f"Password unlocked succesfully for user: '{userLogon}'", inStepMessage=True)

    def updateUserRoleInGroup(self, userLogon, groupName):
        """
        Back office helper class : BO Request Method Call to update the User Role in Group
        userLogon: i.e: test368_wst
        groupName: i.e. L2_Adviser_Transact
        """
        boUser: BOUserObj = self.getBOUserByUserLogon(userLogon)
        if not boUser:
            PrintMessage(f"User '{userLogon}' not found in Back Office. Exit.", inStepMessage=True)
            return False

        userSiteAccessParams = {
            "searchuserid": boUser.userId,
            "type": "edit",
            "searchfirstname": boUser.firstname,
            "searchlastname": boUser.surname,
            "searchadvcode": None}
        userSiteAccessResponseText = self.backOfficeRequests.maintenanceTabUserSiteAccessRequest(method="GET", params=userSiteAccessParams)
        htmlParser = etree.HTMLParser()

        userSiteAccessResponseTree: etree.ElementBase = etree.parse(StringIO(userSiteAccessResponseText), htmlParser)

        # get id for the groupName
        matchingElements = userSiteAccessResponseTree.find(".//select[@id='newpermission']").xpath(f".//option[contains(text(), '{groupName}')]")
        if not matchingElements:
            PrintMessage(f"Failed to find '{groupName}' group name in the list", inStepMessage=True)
            return False

        payload = {
            "actiontype": "modify",
            "type": "edit",
            "searchuserid": boUser.userId,
            "searchusername": None,
            "searchadvcode": None,
            "permissioncount": 1 if boUser.groupName else 0,
            "txtupdateid1": "1731979",  # no idea what this is
            "txtsecsys1": "NEW",  # no idea what this is
            "newpermission": matchingElements[0].get("value"),
            "clientiddup": None,
            "txtinfodup": None,
            "clientiddup2": None,
            "txtinfodup2": None,
            "rbenable": "Enabled"
        }

        userSiteAccessResponseText = self.backOfficeRequests.maintenanceTabUserSiteAccessRequest(method="POST", params=userSiteAccessParams, data=payload)
        userSiteAccessResponseTree: etree.ElementBase = etree.parse(StringIO(userSiteAccessResponseText), htmlParser)
        matchingElements = userSiteAccessResponseTree.xpath("//td[text()='User has been permissioned to the user group specified.']")
        boUserAfterUpdate: BOUserObj = self.getBOUserByUserLogon(userLogon)

        if matchingElements and boUserAfterUpdate.groupName == groupName:
            PrintMessage(f"User: '{userLogon}' succesfully updated with group: '{groupName}'", inStepMessage=True)
            return True
        PrintMessage(f"Failed to update user: '{userLogon}' with group: '{groupName}'", inStepMessage=True)
        return False

    def createUser(self, newUserLogon, newUserPassword, companyName, groupName):
        PrintMessage(f"Creating user: '{newUserLogon}' with companyName: '{companyName}' and groupName: '{groupName}' via BO", inStepMessage=True)
        boUser = BOUserObj()
        boUser.firstname = "PyStorm"
        boUser.surname = "Automation"
        boUser.email = "test1@abrdn.com"
        boUser.country = "New Zealand"
        boUser.company = companyName
        boUser.clienttype = "WRAP"
        boUser.owner = "FNZC"
        boUser.webname = newUserLogon
        boUser.password = newUserPassword
        boUser.confirmPassword = newUserPassword

        saveNewUserPayload = self.getSaveUserDataFill(*self.verificationToken(), boUser=boUser)

        saveNewUserParameters = {
            "type": None,
            "actiontype": "savenew",
            "searchuserid": None
        }

        responseObject = self.backOfficeRequests.maintenanceTabMaintainUserRequest(
            method="POST", params=saveNewUserParameters, data=saveNewUserPayload, responseObject=True)

        matchObj = re.search(r"searchuserid=(\d*)", responseObject.headers["Set-Cookie"])
        if not matchObj:
            PrintMessage(f"Failed to create user with logon: '{newUserLogon}'", inStepMessage=True)
            if "Please+locate+the+user+you+want+to+view" in responseObject.headers.get("Set-Cookie"):
                PrintMessage("User may already exist.", inStepMessage=True)
            return None

        boUser.userId = matchObj.group(1)
        PrintMessage(f"Created user with userId: '{boUser.userId}'", inStepMessage=True)

        userSiteAccessParameters = {"searchuserid": boUser.userId, "type": "edit"}

        userSiteAccessResponseText = self.backOfficeRequests.maintenanceTabUserSiteAccessRequest(method="GET", params=userSiteAccessParameters)
        htmlParser = etree.HTMLParser()

        userSiteAccessResponseTree: etree.ElementBase = etree.parse(StringIO(userSiteAccessResponseText), htmlParser)

        # get id for the groupName
        matchingElements = userSiteAccessResponseTree.find(".//select[@id='newpermission']").xpath(f".//option[contains(text(), '{groupName}')]")
        if not matchingElements:
            PrintMessage(f"Failed to find '{groupName}' group name in the list", inStepMessage=True)
            return None

        userSiteAccessPayload = {
            "actiontype": "modify",
            "type": "edit",
            "searchuserid": boUser.userId,
            "searchusername": None,
            "searchadvcode": None,
            "permissioncount": 0,
            "newpermission": matchingElements[0].get("value"),
            "clientiddup": None,
            "txtinfodup": None,
            "clientiddup2": None,
            "txtinfodup2": None
        }

        userSiteAccessResponseText = self.backOfficeRequests.maintenanceTabUserSiteAccessRequest(
            method="POST", params=userSiteAccessParameters, data=userSiteAccessPayload)
        userSiteAccessResponseTree: etree.ElementBase = etree.parse(StringIO(userSiteAccessResponseText), htmlParser)
        matchingElements = userSiteAccessResponseTree.xpath("//td[text()='User has been permissioned to the user group specified.']")

        if matchingElements:
            PrintMessage(
                f"New user: '{newUserLogon}' succesfully created with userId: '{boUser.userId}', company: '{boUser.company}' and group: '{groupName}'",
                inStepMessage=True)
            return True
        PrintMessage(f"Created user with userId: '{boUser.userId}' but failed to permission to group: '{groupName}'", inStepMessage=True)
        return False

    def firstUserLoginAndPasswordUpdate(self, userName, userPassword, newPassword):
        """
        Method to be used for first time user login
        User is expected to be prompted with password change request
        """
        # extrac current user ID to use it to copy setup, a WORK AROUND iisue where new user has no advisers setup
        # new user: 1572592
        # copied from user: 1567404
        sessionUser: BOUserObj = self.getBOUserByUserLogon(self.sessionUserName)
        newUser: BOUserObj = self.getBOUserByUserLogon(userName)
        params = {"type": "edit",
                  "searchuserid": newUser.userId,
                  "searchfirstname": "PyStorm",
                  "searchlastname": "Automation",
                  "searchadvcode": None}

        data = {"actiontype": "duplicate2",
                "type": "edit",
                "searchuserid": newUser.userId,
                "searchusername": None,
                "searchadvcode": None,
                "permissioncount": "1",
                "txtupdateid1": "1731964",
                "txtsecsys1": "NEW",
                "newpermission": None,
                "clientiddup": None,
                "txtinfodup": None,
                "clientiddup2": sessionUser.userId,
                "txtinfodup2": None,
                "rbenable": "Enabled"}

        PrintMessage(f"BackOfficeUserHelper> copy site permissions from userID: '{sessionUser.userId}' to userId: '{newUser.userId}'", inStepMessage=True)
        copiedSiteSetupResponse = self.backOfficeRequests.maintenanceTabUserSiteAccessRequest(method="POST", params=params, data=data)
        if self.USER_PERMISSIONS_COPIED_MESSAGE in copiedSiteSetupResponse:
            PrintMessage("BackOfficeUserHelper> User site permissions copied succesfully.", inStepMessage=True)
        else:
            PrintMessage("BackOfficeUserHelper> Failed to copy user site permissions!", inStepMessage=True)
            PrintMessage("BackOfficeUserHelper> Exiting...", inStepMessage=True)
            sys.exit(1)

        PrintMessage(f"BackOfficeUserHelper> updating user: '{userName}' with new password", inStepMessage=True)
        session: requests.Session = requests.Session()

        # Make attempt to login
        getLoginResponse = session.request("POST", f"{self.backOfficeUrl}/home.aspx", data={'txtusername': userName, 'txtpassword': userPassword})
        if self.INVALID_USER_PASSWORD_MESSAGE in getLoginResponse.text:
            PrintMessage("BackOfficeUserHelper> Wrong password provided: '{userPassword}' for user: '{userName}'", inStepMessage=True)
            PrintMessage("BackOfficeUserHelper> Exiting...", inStepMessage=True)
            sys.exit(1)

        # Summary for the client
        session.request("GET", f"{self.backOfficeRequests.baseUrl}/clients/holdings/holdings-summarynoclient.aspx")

        # Serve prompt to change password
        url = f"{self.backOfficeRequests.baseUrl}/admin/logindetails/logindetails-changepassword.aspx?UserMsg=PasswordExpired"
        getChangePasswordResponse = session.request("GET", url)

        # Change password
        PrintMessage(f"BackOfficeUserHelper> updating passowrd for user: '{userName}'", inStepMessage=True)
        params = {"UserMsg": "PasswordExpired"}
        parsedHTML = BeautifulSoup(cleanUpRawResponseText(getChangePasswordResponse.text), features="html.parser")
        updatePasswordData = {"__RequestVerificationToken": parsedHTML.body.find("input", attrs={"id": "__RequestVerificationToken"})["value"],
                              "RandomString": parsedHTML.body.find("input", attrs={"id": "RandomString"})["value"],
                              "actiontype": "changepassword",
                              "currentpassword": userPassword,
                              "newpassword": newPassword,
                              "confirmpassword": newPassword}

        requestUrl = f"{self.backOfficeRequests.baseUrl}/admin/logindetails/logindetails-changepassword.aspx?UserMsg=PasswordExpire"
        postChangePasswordResponse = session.request("POST", requestUrl, params=params, data=updatePasswordData)

        if self.PASSWORD_CHANGED_MESSAGE in postChangePasswordResponse.text:
            PrintMessage(f"BackOfficeUserHelper> Password for user: '{userName}' updated succesfully", inStepMessage=True)
        else:
            PrintMessage("BackOfficeUserHelper> Password WAS NOT updated succesfully for user '{userName}'", inStepMessage=True)
