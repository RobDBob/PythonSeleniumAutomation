import operator
from retry import retry
from selenium.webdriver.common.alert import Alert

from CommonCode.CustomExceptions import UIException


class PyStormAlert(Alert):
    @retry(exceptions=UIException, delay=4, tries=5)
    def waitForText(self, expectedText, comparisonOperator: operator = operator.eq):
        if comparisonOperator(expectedText, self.text):
            return
        
        raise UIException(f"Expected alert text: '{expectedText}' got '{self.text}'")
