import argparse
from CommonCode.API.BackOffice.BackOfficeUserHelper import BackOfficeUserHelper
from CommonCode.TestExecute.CommandLineArgumentsParser import CommandLineArgumentsParser
from CommonCode.TestExecute.ExecuteEnums import ConfigOptions
from CommonCode.TestExecute.TestContext import Test_Context


def unlockUserPasswordViaBO():
    boUserName = "test484_opt"
    boUserPassword = "Tester99"

    parser = argparse.ArgumentParser(prefix_chars="-")
    parser.add_argument("-userName", required=True, type=str, help="Provide BO user name to password unblock")
    CommandLineArgumentsParser.addArgumentConfigurationFile(parser)
    parsedArgs = parser.parse_args()
    Test_Context.update(parsedArgs)
    Test_Context.updateFromConfigFile()

    backOfficeUsers = BackOfficeUserHelper(Test_Context.getSetting(ConfigOptions.BACK_OFFICE_URL),
                                           boUserName,
                                           boUserPassword)

    backOfficeUsers.unlockUserPassword(parsedArgs.userName)


if __name__ == "__main__":
    unlockUserPasswordViaBO()
