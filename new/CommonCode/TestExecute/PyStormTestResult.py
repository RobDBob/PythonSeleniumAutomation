from unittest import TextTestResult
from CommonCode.TestExecute import Constants as Const
from CommonCode.TestExecute.Logging import PrintMessage


class PyStormTextTestResult(TextTestResult):
    def stopTest(self, test):
        PrintMessage(f"{Const.TEST_TAIL}\n\r")
        super().stopTest(test)

    def stopTestRun(self):
        PrintMessage(Const.RUN_TAIL)
        super().stopTestRun()
