import argparse
import os
from CommonCode.TestExecute import Constants
from CommonCode.TestExecute.TestContext import TestContext

# Parse Argument messages
BUILD_NUMBER_DEPLOY_MESSAGE = "Optional argument to specify build number."
HOST_ADDRESS = "Host name, IP Address."
TEST_IDS = "Specify single test rail ID."
TEST_CLASS_NAME = "Specify name of the test class, partial name is sufficient. Tests from all matched classes " \
                  "will be executed."
TEST_ATTRIBUTE_NAME = "Specify test attribute name i.e. smoke. All tests matching this attribute will be executed."
RUN_HEADLESS = "Option to tell framework to execute tests in headless mode."
RUN_SHELL_BINARY = "Option to tell framework to shell binary over standard webdriver."
RUN_DEBUG = "Option to tell framework to execute tests in debug mode. " \
            "Used to print out more in depth data (i.e. REST API body request)."
RUN_LUF = "Option to tell framework to execute test in a loop until first failure"
TEST_FOLDER = "Specify test search folder"
GATHER_SCREENSHOOT_EVIDENCE = "Switch, when on, instructs framework to gather screenshot evidence at implemented steps."
CAPTURE_NETWORK_LOGS = "Switch, when on, instructs framework to capture network logs."
DRY_RUN = "Switch, when on, instructs framework to run SKIP upload test results to ADO."
RE_RUN_FAILED = "Switch, when on, instructs framework to re run failed tests."
TEST_CLASS_NAME_OR_TEST_CASE_ID = "Required either test class name(s) or test case ID(s)."
RUN_CONFIG_SELECTION = "Configuration file used during test execution."
TEST_PLAN = "Specify ADO test plan where test suite resides"
REPORT_HYPERLINK_MESSAGE = "Specify link to be included in tes report."


class CommandLineArgumentsParser:
    @staticmethod
    def getAvailableConfigFiles(prefix, postfix):
        """
        Configuration files are expected to be in format TestRunConfig_XYZ.json
        The TestRunConfig_ and .json are stripped off.
        :param prefix:
        :param postfix:
        :return:
        """
        availableConfigFields = []

        for configFile in os.listdir("./ConfigFiles"):
            if configFile.startswith(prefix) and configFile.endswith(postfix):

                # 14:-5 remove TestRunConfig_ and .json
                availableConfigFields.append(configFile[14:-5])

        return availableConfigFields

    @staticmethod
    def addArgumentConfigurationFile(parser: argparse.ArgumentParser):
        configFiles = CommandLineArgumentsParser.getAvailableConfigFiles("TestRunConfig_", ".json")

        parser.add_argument("-c",
                            dest="CURRENT_CONFIG_NAME",
                            help=RUN_CONFIG_SELECTION,
                            choices=configFiles,
                            required=True)

    @staticmethod
    def addArgumentTestPlan(parser: argparse.ArgumentParser):
        parser.add_argument("-testPlan",
                            dest="TEST_PLAN",
                            help=TEST_PLAN)

    @staticmethod
    def addArgumentBuildNumber(parser: argparse.ArgumentParser):
        parser.add_argument("-b",
                            dest="buildNumber",
                            help=BUILD_NUMBER_DEPLOY_MESSAGE,
                            type=int,
                            default=None)

    @staticmethod
    def addArgumentListOfTestIDs(parser: argparse.ArgumentParser):
        parser.add_argument("-t",
                            nargs="*",
                            dest="TEST_IDS",
                            type=int,
                            help=TEST_IDS,
                            default=[])

    @staticmethod
    def addArgumentListOfClassNames(parser: argparse.ArgumentParser):
        parser.add_argument("-class",
                            nargs="*",
                            dest="TEST_CLASS_NAMES",
                            type=str,
                            help=TEST_CLASS_NAME,
                            default=[])

    @staticmethod
    def addArgumentTestAttribute(parser: argparse.ArgumentParser):
        """
        For now and simplicity we only support a single parameter
        :param parser:
        :return:
        """
        parser.add_argument("-attribute",
                            dest="TEST_ATTRIBUTE",
                            type=str,
                            help=TEST_ATTRIBUTE_NAME,
                            default=None)

    @staticmethod
    def addArgumentRunHeadless(parser: argparse.ArgumentParser):
        parser.add_argument("--headless",
                            dest="RUN_HEADLESS",
                            default=False,
                            help=RUN_HEADLESS,
                            action="store_true")

    @staticmethod
    def addArgumentUseChromeBinary(parser: argparse.ArgumentParser):
        parser.add_argument("--shellBinary",
                            dest="RUN_SHELL_BINARY",
                            default=False,
                            help=RUN_SHELL_BINARY,
                            action="store_true")

    @staticmethod
    def addArgumentLoopUntilFailure(parser: argparse.ArgumentParser):
        parser.add_argument("--luf",
                            dest="LUF",
                            default=False,
                            help=RUN_LUF,
                            action="store_true")

    @staticmethod
    def addArgumentSearchFolder(parser: argparse.ArgumentParser):
        parser.add_argument("-testFolder",
                            dest="TEST_FOLDER",
                            help=TEST_FOLDER,
                            default=Constants.DEFAULT_REGRESSION_FOLDER)

    @staticmethod
    def addArgumentGatherScreenshotEvidence(parser: argparse.ArgumentParser):
        parser.add_argument("--gatherScreenshotEvidence",
                            dest="GATHER_SCREENSHOT_EVIDENCE",
                            help=GATHER_SCREENSHOOT_EVIDENCE,
                            default=False,
                            action="store_true")

    @staticmethod
    def addArgumentGatherCaptureNetworkLogs(parser: argparse.ArgumentParser):
        parser.add_argument("--captureNetworkLogs",
                            dest="CAPTURE_NETWORK_LOGS",
                            help=CAPTURE_NETWORK_LOGS,
                            default=False,
                            action="store_true")

    @staticmethod
    def addArgumentUploadTestResultsToAdo(parser: argparse.ArgumentParser):
        parser.add_argument("--dryRun",
                            dest="DRY_RUN",
                            help=DRY_RUN,
                            default=False,
                            action="store_true")

    @staticmethod
    def addArgumentReRunFailedTests(parser: argparse.ArgumentParser):
        parser.add_argument("--reRunFailed",
                            dest="RE_RUN_FAILED",
                            help=RE_RUN_FAILED,
                            default=False,
                            action="store_true")

    @staticmethod
    def validateTestParameters(parser: argparse.ArgumentParser, parsedArgs):
        if len(parsedArgs.TEST_IDS) == 0 and len(parsedArgs.TEST_CLASS_NAMES) == 0 and not parsedArgs.TEST_ATTRIBUTE:
            parser.error(TEST_CLASS_NAME_OR_TEST_CASE_ID)

    @staticmethod
    def processArgumentsSingleTestRun(testContext: TestContext):
        """
        Method to arrange standard argument options.
        It allows test framework to utilize its own parser with additional options on top of the standard ones.
        :param testContext:
        :return:
        """
        parser = argparse.ArgumentParser(prefix_chars="-")

        CommandLineArgumentsParser.addArgumentConfigurationFile(parser)
        CommandLineArgumentsParser.addArgumentListOfTestIDs(parser)
        CommandLineArgumentsParser.addArgumentListOfClassNames(parser)
        CommandLineArgumentsParser.addArgumentTestAttribute(parser)
        CommandLineArgumentsParser.addArgumentRunHeadless(parser)
        CommandLineArgumentsParser.addArgumentUseChromeBinary(parser)
        CommandLineArgumentsParser.addArgumentLoopUntilFailure(parser)
        CommandLineArgumentsParser.addArgumentSearchFolder(parser)
        CommandLineArgumentsParser.addArgumentGatherScreenshotEvidence(parser)
        CommandLineArgumentsParser.addArgumentGatherCaptureNetworkLogs(parser)

        parsedArgs = parser.parse_args()

        CommandLineArgumentsParser.validateTestParameters(parser, parsedArgs)

        testContext.update(parsedArgs)
        testContext.updateFromConfigFile()

    @staticmethod
    def processArgumentsMultiDayTestRun(testContext: TestContext):
        """
        Method to arrange standard argument options.
        It allows test framework to utilize its own parser with additional options on top of the standard ones.
        :param testContext:
        :return:
        """
        parser = argparse.ArgumentParser(prefix_chars="-")

        CommandLineArgumentsParser.addArgumentTestPlan(parser)
        CommandLineArgumentsParser.addArgumentConfigurationFile(parser)
        CommandLineArgumentsParser.addArgumentRunHeadless(parser)
        CommandLineArgumentsParser.addArgumentSearchFolder(parser)
        CommandLineArgumentsParser.addArgumentGatherScreenshotEvidence(parser)

        parsedArgs = parser.parse_args()

        testContext.update(parsedArgs)
        testContext.updateFromConfigFile()

    @staticmethod
    def processArgumentsGroupTestRun(testContext: TestContext):
        """
        This method is used by the RunAll, RunRegression, RunSmoke, RunQuick

        Method to arrange standard argument options.
        It allows test framework to utilize its own parser with additional options on top of the standard ones.
        :param parser:
        :return:
        """
        parser = argparse.ArgumentParser(prefix_chars="-")

        CommandLineArgumentsParser.addArgumentConfigurationFile(parser)
        CommandLineArgumentsParser.addArgumentTestPlan(parser)
        CommandLineArgumentsParser.addArgumentBuildNumber(parser)
        CommandLineArgumentsParser.addArgumentUseChromeBinary(parser)
        CommandLineArgumentsParser.addArgumentSearchFolder(parser)
        CommandLineArgumentsParser.addArgumentGatherScreenshotEvidence(parser)
        CommandLineArgumentsParser.addArgumentUploadTestResultsToAdo(parser)
        CommandLineArgumentsParser.addArgumentReRunFailedTests(parser)

        parsedArgs = parser.parse_args()

        testContext.update(parsedArgs)
        testContext.updateFromConfigFile()

    @staticmethod
    def processArgumentsEnvironmentSelection(testContext: TestContext):
        parser = argparse.ArgumentParser(prefix_chars="-")

        CommandLineArgumentsParser.addArgumentConfigurationFile(parser)
        parsedArgs = parser.parse_args()
        testContext.update(parsedArgs)
        testContext.updateFromConfigFile()

    @staticmethod
    def processArgumentsForBackOfficeUserCreation(testContext: TestContext):
        parser = argparse.ArgumentParser(prefix_chars="-")

        parser.add_argument("-userName", required=True, type=str, help="Provide Name for new user")
        parser.add_argument("-userCompany", required=True, type=str, help="Provide Company for new user")
        parser.add_argument("-userGroup", required=True, type=str, help="Provide Group name for new user")

        CommandLineArgumentsParser.addArgumentConfigurationFile(parser)
        parsedArgs = parser.parse_args()
        testContext.update(parsedArgs)
        testContext.updateFromConfigFile()
        return parsedArgs
