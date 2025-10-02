import sys
from CommonCode.API.BackOffice.BackOfficeUserHelper import BackOfficeUserHelper
from CommonCode.API.Wrap.PlatformRequestsUserFirstLogin import PlatformRequestsUserFirstLogin
from CommonCode.TestExecute.CommandLineArgumentsParser import CommandLineArgumentsParser
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.TestContext import Test_Context

INTERMITENT_PASSWORD = "Tester11"
FINAL_PASSWORD = "Tester99"

BO_USER_NAME = "test484_opt"
BO_USER_PASSWORD = "Tester99"


def createUserViaBO():
    """
    Users defaults to Tester99 password
    For Platform user:
        userLogon = i.e. todelete7_wst
        companyName = SLIFE
        groupName = i.e. L2_Adviser_Transact
    For BO User:
        userLogon = i.e. todelete7_wst
        companyName = FNZS
        groupName = i.e. UKWrapSupport_FullAdmin

    """
    parsedArgs = CommandLineArgumentsParser.processArgumentsForBackOfficeUserCreation(Test_Context)
    userName: str = parsedArgs.userName

    assert userName.endswith("_wst") or parsedArgs.userName.endswith("_opt"), "expected user name to end with either _opt or _wst"

    backOfficeUsers = BackOfficeUserHelper(Test_Context.getSetting(ConfigOptions.BACK_OFFICE_URL),
                                           BO_USER_NAME,
                                           BO_USER_PASSWORD)
    if not backOfficeUsers.createUser(userName, INTERMITENT_PASSWORD, parsedArgs.userCompany, parsedArgs.userGroup):
        PrintMessage("BackOfficeUserHelper> Exiting...")
        sys.exit(1)

    if userName.endswith("opt"):
        backOfficeUsers.firstUserLoginAndPasswordUpdate(userName, INTERMITENT_PASSWORD, FINAL_PASSWORD)

    if userName.endswith("wst"):
        platformHelper = PlatformRequestsUserFirstLogin(Test_Context.getSetting(ConfigOptions.SLWRAP_API_URL))
        platformHelper.firstUserLoginAndPasswordUpdate(userName, INTERMITENT_PASSWORD, FINAL_PASSWORD)


if __name__ == "__main__":
    createUserViaBO()
