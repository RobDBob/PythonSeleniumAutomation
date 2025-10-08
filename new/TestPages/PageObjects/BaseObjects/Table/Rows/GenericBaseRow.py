from selenium.webdriver.common.by import By
from CommonCode.Driver.PyStormElement import PyStormElement
from TestPages.PageObjects.BaseObjects.BaseTestObject import BaseTestObject


class GenericBaseRow(BaseTestObject):
    CELL_LOCATOR = (By.XPATH, ".//td[@class]")

    def getCell(self, index) -> PyStormElement:
        cellElements = self.element.find_elements(*self.CELL_LOCATOR)
        if cellElements and len(cellElements) > index:
            return cellElements[index]