from CommonCode.TestExecute.Logging import PrintMessage


class BasePage(object):
    def __init__(self, webdriver):
        self.webdriver = webdriver

    def navigate(self):
        return

    def wait(self):
        return

    def load(self, page, refresh=True):
        if refresh:
            PrintMessage("Refreshing...")
            self.webdriver.refresh()
        PrintMessage("Loading...%s" % page)
        self.navigate()
        self.wait()
