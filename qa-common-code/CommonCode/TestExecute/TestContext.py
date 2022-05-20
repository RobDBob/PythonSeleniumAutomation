import logging
import os
import traceback

import yaml

from CommonCode.JsonReader import JsonReader
from CommonCode.constants import magic_repo_MAIN_URL


class TestContext(object):
    """
    Bridge class between test runner and unittest
    It contains test environment information
    """
    current_config_file_name = None

    # holds information about currently deployed build number
    build_number = None
    run_headless = True
    run_debug = False
    api_session_token = None
    test_user = None
    report_recipients = None

    # to support multiprocessor test run
    log_name = 'testLog'

    def __copy__(self):
        new_one = type(self)()
        new_one.__dict__.update(self.__dict__)
        return new_one

    def _dir(self, obj):
        """
        Same as dir with exception, it'll ignore internal variables
        :param obj:
        :return:
        """
        return [k for k in dir(obj) if not k.startswith('_') and getattr(type(obj), k, None) in [False, True, None]]

    def update(self, obj):
        """
        Updated test context with values set in incoming obj
        This is used with either another TestContext or ParsedArgs
        :param obj:
        :return:
        """
        logger = logging.getLogger(self.log_name)

        if obj is None:
            logger.info(f"Nothing to set in TestContext.Update - returning")
            return

        for attribute in self._dir(obj):
            value_to_set = getattr(obj, attribute)

            try:
                setattr(self, attribute, value_to_set)
                logger.info(f"Set TestContext attribute {attribute} to {value_to_set}")
            except AttributeError as e:
                tb = traceback.format_exc()
                logger.info('Encountered exception {0}, with args {1}'.format(type(e), e.args))
                logger.info("traceback: {0}".format(tb))
                logger.info(f"FAILED to set TestContext attribute {attribute} to {value_to_set}")
                pass

    def get_required_folder(self, folder_name):
        try:
            return self.environment_config['required_folders'][folder_name]
        except KeyError:
            return None

    @property
    def run_config(self):
        run_config_path = f'./ConfigFiles/TestRunConfig_{self.current_config_file_name}.json'

        if os.path.exists(run_config_path):
            return JsonReader(run_config_path)
        return None

    @property
    def test_rail_config(self):
        test_rail_config_path = "./ConfigFiles/TestReportConfig.json"

        if os.path.exists(test_rail_config_path):
            config_file = JsonReader(test_rail_config_path)
            return config_file.load("TestRailConnection")
        return None

    @property
    def environment_config(self):
        env_config_path = './ConfigFiles/EnvironmentConfig.yaml'

        if os.path.exists(env_config_path):
            with open(env_config_path) as yamlfile:
                return yaml.full_load(yamlfile)
        return None

    @property
    def report_hyper_link(self):
        if hasattr(self, 'magic_repo_link'):
            link = magic_repo_MAIN_URL + self.magic_repo_link
            return f'<a href="{link}">magic_repo test results.</a>'
        return ''


# global Test_Context
Test_Context = TestContext()
