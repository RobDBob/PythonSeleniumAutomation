from lxml import etree
from CommonCode.TestExecute.Logging import PrintMessage

# pylint: disable = I1101:c-extension-no-member


class BOUserObj:
    siteAccessTable: etree.ElementBase = None
    firstname = None
    surname = None
    email = None
    country = None
    company = None
    clienttype = None
    owner = None
    webname = None
    userSiteAccessDisabled = None
    userPasswordLocked = None
    userId = None
    userType = None
    password = None
    confirmPassword = None

    def _getValueFromData(self, data: etree.ElementBase, xpath: str):
        """"""
        elements: list[etree.ElementBase] = data.xpath(xpath)
        if elements:
            return elements[0].get("value")
        return None

    def _getTextFromData(self, data: etree.ElementBase, xpath: str):
        """"""
        elements: etree.ElementBase = data.xpath(xpath)
        if elements:
            return elements[0].text
        return None

    def getUserTypeForSite(self, siteName='Standard Life Wrap'):
        """
        returns user type for Standard Life Wrap site
        """
        xpathElement = self._siteAccessTable.xpath(f".//td[@class='TableData' and text()='{siteName}']/following-sibling::td")
        if xpathElement:
            return xpathElement[0].text
        PrintMessage(f"BOUserObj > userType not found for site {siteName}")
        return None

    def updateFromResponses(self, userEditTableElement: etree.ElementBase, userSiteAccessTableElement: etree.ElementBase):
        """
        update the user object with the new data
        """
        self.siteAccessTable = userSiteAccessTableElement.xpath("//td[@class='TableSubHead' and text()='Site']//ancestor::table")[-1]

        self.firstname = self._getValueFromData(userEditTableElement, ".//td[contains(text(), 'First Name')]//following-sibling::td/input")
        self.surname = self._getValueFromData(userEditTableElement, ".//td[contains(text(), 'Surname')]//following-sibling::td/input")
        self.email = self._getValueFromData(userEditTableElement, ".//td[contains(text(), 'Email Address')]//following-sibling::td/input")
        self.country = self._getValueFromData(userEditTableElement, ".//td[contains(text(), 'Country')]//following-sibling::td/select/option[@selected]")
        self.company = self._getValueFromData(userEditTableElement, ".//td[contains(text(), 'Company')]//following-sibling::td/select/option[@selected]")
        self.clienttype = self._getValueFromData(userEditTableElement, ".//td[contains(text(), 'Client Type')]//following-sibling::td/option[@selected]")
        self.owner = self._getValueFromData(userEditTableElement, ".//td[contains(text(), 'Owner')]//following-sibling::td/option[@selected]")
        self.webname = self._getValueFromData(userEditTableElement, ".//td[contains(text(), 'User Name')]//following-sibling::td/input")

        self.userSiteAccessDisabled = bool("DISABLED" in userEditTableElement.xpath(".//td[contains(text(), 'Site Access Status')]//parent::tr/descendant::*/text()"))
        self.userPasswordLocked = bool("LOCKED" in userEditTableElement.xpath(".//td[contains(text(), 'Password Status')]//parent::tr/descendant::*/text()"))
        self.userId = self._getTextFromData(userEditTableElement, ".//td[contains(text(), 'User ID')]//following-sibling::td")
        self.userType = self._getTextFromData(userSiteAccessTableElement, ".//td[@class='TableData' and text()='Standard Life Wrap']/following-sibling::td")

    @property
    def groupName(self):
        """
        returns user group name
        """
        headerElements = [k.text for k in self.siteAccessTable.xpath(".//td[@class='TableSubHead']")]
        if not headerElements:
            PrintMessage("BOUserObj > groupName not found in site access table headers")
            return None
        groupNameHeaderIndex = headerElements.index("Group Name")
        dataElements = [k.text for k in self.siteAccessTable.xpath(".//td[@class='TableData']")]
        if not dataElements:
            PrintMessage("BOUserObj > groupName not found in site access table data")
            return None
        return dataElements[groupNameHeaderIndex] if groupNameHeaderIndex < len(dataElements) else None
