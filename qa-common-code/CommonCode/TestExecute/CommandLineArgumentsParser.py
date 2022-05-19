import argparse
import os

from CommonCode.Enums_Utils import list_parameters
from CommonCode.TestExecute.ExecuteEnums import AutomationTypeEnum

# Parse Argument messages
BUILD_NUMBER_DEPLOY_MESSAGE = 'Optional argument to specify build number.'
HOST_ADDRESS = 'Host name, IP Address.'
REPORT_RECIPIENTS_MESSAGE = 'String parameter listing email recipients, comma delimited.'
TEST_IDS = 'Specify single test rail ID.'
TEST_CLASS_NAME = 'Specify name of the test class, partial name is sufficient. Tests from all matched classes ' \
                  'will be executed.'
TEST_ATTRIBUTE_NAME = 'Specify test attribute name i.e. smoke. All tests matching this attribute will be executed.'
RUN_HEADLESS = 'Option to tell framework to execute tests in headless mode.'
RUN_DEBUG = 'Option to tell framework to execute tests in debug mode. ' \
            'Used to print out more in depth data (i.e. REST API body request).'
RUN_LUF = 'Option to tell framework to execute test in a loop until first failure'
TestClassNameOrTestCaseID = 'Required either test class name(s) or test case ID(s).'
RUN_CONFIG_SELECTION = 'Configuration file used during test execution.'
REPORT_HYPERLINK_MESSAGE = 'Specify link to be included in tes report.'
AUTOMATION_TYPE_MESSAGE = 'Specify automation type, this parameter might be skipped. Default value is None (eq to all).'
BROWSER_STACK_MESSAGE = 'Executes given test IDs on browserstack when set'


class CommandLineArgumentsParser(object):
    @staticmethod
    def get_available_config_files(prefix, postfix):
        """
        Configuration files are expected to be in format TestRunConfig_XYZ.json
        The TestRunConfig_ and .json are stripped off.
        :param prefix:
        :param postfix:
        :return:
        """
        available_config_fields = []

        for config_file in os.listdir('./ConfigFiles'):
            if config_file.startswith(prefix) and config_file.endswith(postfix):

                # 14:-5 remove TestRunConfig_ and .json
                available_config_fields.append(config_file[14:-5])

        return available_config_fields

    @staticmethod
    def read_default_config():
        default_config = None
        try:
            with open('./ConfigFiles/default_config') as f:
                default_config = f.readline()

        except IOError:
            default_config = None
        finally:
            return default_config

    @staticmethod
    def add_argument_configuration_file(parser):
        config_files = CommandLineArgumentsParser.get_available_config_files('TestRunConfig_', '.json')
        default_config = CommandLineArgumentsParser.read_default_config()

        parser.add_argument('-c',
                            dest='current_config_file_name',
                            help=RUN_CONFIG_SELECTION,
                            choices=config_files,
                            default=default_config,
                            required=True)

    @staticmethod
    def add_argument_build_number(parser):
        parser.add_argument("-b",
                            dest='build_number',
                            help=BUILD_NUMBER_DEPLOY_MESSAGE,
                            type=int,
                            default=None)

    @staticmethod
    def add_argument_list_of_report_recipients(parser):
        parser.add_argument('-r',
                            nargs='*',
                            dest='report_recipients',
                            help=REPORT_RECIPIENTS_MESSAGE,
                            default=[])

    @staticmethod
    def add_argument_list_of_test_ids(parser):
        parser.add_argument('-t',
                            nargs='*',
                            dest='test_ids',
                            type=int,
                            help=TEST_IDS,
                            default=[])

    @staticmethod
    def add_argument_list_of_class_names(parser):
        parser.add_argument('-class',
                            nargs='*',
                            dest='test_class_names',
                            type=str,
                            help=TEST_CLASS_NAME,
                            default=[])

    @staticmethod
    def add_argument_test_attribute(parser):
        """
        For now and simplicity we only support a single parameter
        :param parser:
        :return:
        """
        parser.add_argument('-attribute',
                            dest='test_attribute',
                            type=str,
                            help=TEST_ATTRIBUTE_NAME,
                            default=None)

    @staticmethod
    def add_argument_run_headless(parser):
        parser.add_argument('--headless',
                            dest='run_headless',
                            default=False,
                            help=RUN_HEADLESS,
                            action='store_true')

    @staticmethod
    def add_argument_print_debug(parser):
        parser.add_argument('--debug',
                            dest='run_debug',
                            default=False,
                            help=RUN_DEBUG,
                            action='store_true')

    @staticmethod
    def add_argument_loop_until_failure(parser):
        parser.add_argument('--luf',
                            dest='luf',
                            default=False,
                            help=RUN_LUF,
                            action='store_true')

    @staticmethod
    def add_argument_report_hyperlink(parser):
        parser.add_argument("-l",
                            dest='nexus_link',
                            help=REPORT_HYPERLINK_MESSAGE,
                            type=str,
                            default='')

    @staticmethod
    def add_argument_automation_type(parser):
        parser.add_argument("-automation_type",
                            dest='automation_type',
                            help=AUTOMATION_TYPE_MESSAGE,
                            type=str,
                            choices=list_parameters(AutomationTypeEnum),
                            default=None)

    @staticmethod
    def add_argument_browser_stack_execution(parser):
        """
        Trigger for single test execution
        :param parser:
        :return:
        """
        parser.add_argument("--browser_stack",
                            dest='browser_stack',
                            help=BROWSER_STACK_MESSAGE,
                            default=False,
                            action='store_true')

    @staticmethod
    def process_arguments_single_test_run(parser=None):
        """
        Method to arrange standard argument options.
        It allows test framework to utilize its own parser with additional options on top of the standard ones.
        :param parser:
        :return:
        """
        if parser is None:
            parser = argparse.ArgumentParser(prefix_chars='-')

        CommandLineArgumentsParser.add_argument_configuration_file(parser)
        CommandLineArgumentsParser.add_argument_list_of_test_ids(parser)
        CommandLineArgumentsParser.add_argument_list_of_class_names(parser)
        CommandLineArgumentsParser.add_argument_test_attribute(parser)
        CommandLineArgumentsParser.add_argument_run_headless(parser)
        CommandLineArgumentsParser.add_argument_print_debug(parser)
        CommandLineArgumentsParser.add_argument_loop_until_failure(parser)
        CommandLineArgumentsParser.add_argument_browser_stack_execution(parser)

        parsed_args = parser.parse_args()

        if len(parsed_args.test_ids) == 0 and len(parsed_args.test_class_names) == 0 and not parsed_args.test_attribute:
            parser.error(TestClassNameOrTestCaseID)

        return parsed_args

    @staticmethod
    def process_arguments_group_test_run(parser=None):
        """
        This method is used by the RunAll, RunRegression, RunSmoke, RunQuick

        Method to arrange standard argument options.
        It allows test framework to utilize its own parser with additional options on top of the standard ones.
        :param parser:
        :return:
        """
        if parser is None:
            parser = argparse.ArgumentParser(prefix_chars='-')

        CommandLineArgumentsParser.add_argument_configuration_file(parser)
        CommandLineArgumentsParser.add_argument_build_number(parser)
        CommandLineArgumentsParser.add_argument_list_of_report_recipients(parser)
        CommandLineArgumentsParser.add_argument_report_hyperlink(parser)
        CommandLineArgumentsParser.add_argument_automation_type(parser)
        CommandLineArgumentsParser.add_argument_browser_stack_execution(parser)

        parsed_args = parser.parse_args()

        return parsed_args
