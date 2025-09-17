from selenium.webdriver.remote.switch_to import SwitchTo
from CommonCode.Driver.PyStormAlert import PyStormAlert


class PyStormSwitchTo(SwitchTo):
    @property
    def alert(self) -> PyStormAlert:
        """Switches focus to an alert on the page.

        :Usage:
            ::

                alert = driver.switch_to.alert
        """
        alert = PyStormAlert(self._driver)
        _ = alert.text
        return alert
