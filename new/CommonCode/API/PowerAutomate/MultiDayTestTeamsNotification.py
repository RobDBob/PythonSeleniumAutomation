import os
from CommonCode.API.ADORequests import AccessTokenEnum, ADORequests
from CommonCode.API.PowerAutomate.PowerAutomateWrapper import PowerAutomateWrapper
from StandAlone.MultiDayTests.MultiDayTestObjs import TestObj


class MultiDayTestTeamsNotification(PowerAutomateWrapper):
    """
    MultiDay test Report notification to Teams via PowerAutomate
    """

    def __init__(self):
        self.powerAutomateURL = os.environ.get("PA_URL_MULTIDAY_TEST_RESULTS_NOTIFICATION")

    def sendTeamsNotification(self, testObj: TestObj):
        runDetails = ADORequests(AccessTokenEnum.TEST_PLAN_READ_ACCESS_TOKEN).getRunDetails(testObj.runId)
        jsonLoad = {
            "headerTestId": testObj.headerTestId,
            "currentStageTestId": testObj.currentStageTestId,
            "runUrl": runDetails.get("webAccessUrl")
        }

        self.sendToPowerAutomateFlow(jsonLoad)


if __name__ == "__main__":
    from StandAlone.MultiDayTests import MultiDayConst
    testInstructions = {
        MultiDayConst.HEADER_TEST_ID: 1,
        MultiDayConst.STAGES: 2
    }
    testObj = TestObj(testInstructions)
    testObj.runId = 2641307
    testObj.currentStageTestId = 2

    teamsNotifications = MultiDayTestTeamsNotification()
    teamsNotifications.sendTeamsNotification(testObj)
