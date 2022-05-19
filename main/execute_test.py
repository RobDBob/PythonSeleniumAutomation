#!/usr/bin/env python
import os

from CommonCode.TestExecute.CommandLineArgumentsParser import CommandLineArgumentsParser
from CommonCode.TestExecute.RunManager import RunManager
from RunUIAutomation import start_browserstack_session

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    parsed_args = CommandLineArgumentsParser.process_arguments_single_test_run()

    with RunManager(parsed_args) as test_runner:
        start_browserstack_session()
        test_runner.execute_tests_on_demand()
