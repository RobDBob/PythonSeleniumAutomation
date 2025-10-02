import json
import os
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.RunManager import RunManager
from CommonCode.TestExecute.TestContext import Test_Context
from StandAlone.DataInsertionPOC import DataInsertionConsts
from StandAlone.DataInsertionPOC.DataInsertion import DataInsertion
from StandAlone.DataInsertionPOC.ProcessData import processDataIntoClientObject


def getClientDataFromJsonFile(sourceFilePath):
    with open(sourceFilePath, encoding="utf-8") as f:
        return processDataIntoClientObject(json.load(f))


def sortOutConfiguration():
    isPipelineRun = os.environ.get(DataInsertionConsts.ENV_PIPELINE_RUN, "").lower() == "true"

    if isPipelineRun:
        loginType = os.environ.get(DataInsertionConsts.ENV_LOGIN_TYPE)
        loginUrl = os.environ.get(DataInsertionConsts.ENV_LOGIN_URL)
        loginName = os.environ.get(DataInsertionConsts.ENV_USER_NAME)
        loginPassword = os.environ.get(DataInsertionConsts.ENV_USER_PASSWORD)

        Test_Context.setSetting(ConfigOptions.RUN_HEADLESS, True)
        Test_Context.setSetting(ConfigOptions.DOCKER_RUN, True)
    else:
        loginType = DataInsertionConsts.LOGIN_TYPE_INTERNAL
        # loginUrl = "https://slrebrandsyst.fnz.co.uk/fnzhome.aspx"
        loginUrl = "https://slwrapte5.fnz.co.uk/fnzhome.aspx"
        loginName = "test51_wst"
        loginPassword = "Tester99"

        Test_Context.setSetting(ConfigOptions.RUN_HEADLESS, False)
        Test_Context.setSetting(ConfigOptions.DRIVER_PATH, "C:\\webdriver\\chromedriver.exe")

    # setting url to one provided via pipeline
    Test_Context.setSetting(ConfigOptions.BATEMAN_URL, loginUrl)
    Test_Context.setSetting(ConfigOptions.SLWRAP_SITE_URL, loginUrl)

    Test_Context.setSetting(ConfigOptions.GATHER_SCREENSHOT_EVIDENCE, True)

    # instatianates run manager to ensure folders and etc are created
    RunManager.createFrameworkFolders(Test_Context)

    PrintMessage(f"ClientOnboarding configuration, pipeline run: '{isPipelineRun}'")
    PrintMessage(f"\n loginName: {loginName}")
    PrintMessage(f"\n loginPassword length: {len(loginPassword)}")

    PrintMessage(f"\n userLoginType: '{loginType}'")
    PrintMessage(f"\n loginUrl: {loginUrl} \n")

    return loginName, loginPassword, loginType


def f2():
    # for local run:
    # sourceFilePath = os.path.join("StandAlone", "DataInsertionPOC", "bulk_newTemplate_001_cases.json")

    # source file name is set in pipeline
    sourceJsonFileName = "ClientOnboardinSourceFile.json"
    loginName, loginPassword, userLoginType = sortOutConfiguration()
    PrintMessage("start 1")

    srcData = getClientDataFromJsonFile(sourceJsonFileName)
    PrintMessage(f"Source data received: len(): {len(srcData)}")

    dataInsertion = DataInsertion(loginName, loginPassword, userLoginType)
    dataInsertion.runWithData(srcData)


if __name__ == "__main__":
    f2()
