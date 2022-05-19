import json

import requests
from requests.auth import HTTPBasicAuth

from CommonCode.Enums_Utils import LoggingLevel
from CommonCode.TestExecute.ExecuteEnums import AutomationTypeEnum
from CommonCode.TestExecute.Logging import PrintMessage


class TestRailAPIClient(object):
    def __init__(self, host_address, user_name, password):
        self.user = user_name
        self.password = password
        if not host_address.endswith('/'):
            host_address += '/'

        self.base_url = host_address + 'index.php?/api/v2/'

    def get(self, uri):
        url = self.base_url + uri
        header = {'Content-Type': 'application/json'}

        PrintMessage("Sending request to URL: {0}".format(url))

        #  trust_env works around issue with proxy in windows
        #  so far it does not have any negative impact on vagrant test execution
        #  https://stackoverflow.com/questions/28521535/requests-how-to-disable-bypass-proxy
        session = requests.Session()
        session.trust_env = False
        response = session.get(url=url, headers=header, auth=HTTPBasicAuth(self.user, self.password))

        if response.status_code != 200:
            PrintMessage("API non-200 response (HTTP-{0}), reason: {1}".format(response.status_code, response.text))

        response_data = response.json()
        PrintMessage("Request response data: \n{0}\n".format(response_data), LoggingLevel.debug)

        if 'error' not in response_data:
            return response_data

    def post(self, uri, data):
        url = self.base_url + uri
        header = {'Content-Type': 'application/json'}

        json_data = json.dumps(data)
        PrintMessage("Sending request to URL: {0}".format(url))
        PrintMessage("Request data: \n{0}\n".format(json_data), LoggingLevel.debug)

        #  trust_env works around issue with proxy in windows
        #  so far it does not have any negative impact on vagrant test execution
        #  https://stackoverflow.com/questions/28521535/requests-how-to-disable-bypass-proxy
        session = requests.Session()
        session.trust_env = False
        response = session.post(url=url, data=json_data, headers=header, auth=HTTPBasicAuth(self.user, self.password))

        if response.status_code != 200:
            PrintMessage("API non-200 response, reason: {0}".format(response.text))

        response_data = response.json()
        PrintMessage("Request response data: \n{0}\n".format(response_data), LoggingLevel.debug)

        return response_data

    #
    # expected data in dictionary format:
    # {'version': <string>, 'status_id': <string>, 'comment': <string>}
    #

    def _post_results_for_test_case(self, test_run_id, test_id, data):
        rest_url = 'add_result_for_case/{0}/{1}'.format(test_run_id, test_id)

        try:
            self.post(rest_url, data)
        except requests.HTTPError:
            PrintMessage("Test case: {0} not included in test run: {1}.".format(test_id, test_run_id))

    # expects in all_test_results
    # index 0: test status id (pass / failed etc)
    # index 1: test comment
    # index 2: defect
    def post_test_results(self, tested_build_version, test_run_id, all_test_results):
        for test_id in all_test_results:
            test_status_id = all_test_results[test_id][0]
            test_comment = all_test_results[test_id][1]
            test_defect = all_test_results[test_id][2]

            data = {'version': str(tested_build_version),
                    'defects': test_defect,
                    'status_id': test_status_id,
                    'comment': test_comment}
            self._post_results_for_test_case(test_run_id, test_id, data)

    def get_list_of_tests_for_run_id(self, test_run_id, status_id=None):
        assert type(test_run_id) == int, 'Expected int value for the test run id.'

        rest_url = 'get_tests/{0}'.format(test_run_id)
        if status_id:
            assert isinstance(status_id, list)
            statuses = ','.join(map(str, status_id))
            rest_url += '&status_id={0}'.format(statuses)
        return self.get(rest_url)

    def get_results_for_run(self, test_run_id, limit=None, offset=None, created_after=None, status_id=None):
        assert type(test_run_id) == int, 'Expected int value for the test run id.'

        rest_url = 'get_results_for_run/{0}'.format(test_run_id)
        if limit:
            rest_url += '&limit={0}'.format(limit)
        if offset:
            rest_url += '&offset={0}'.format(offset)
        if created_after:
            rest_url += '&created_after={0}'.format(created_after)
        if status_id:
            assert isinstance(status_id, list)
            statuses = ','.join(map(str, status_id))
            rest_url += '&status_id={0}'.format(statuses)
        return self.get(rest_url)

    #
    # test_id =/= test_case_id
    #
    def get_test_result(self, test_id, limit=None):
        """

        :param test_id:
        :param limit:
        :return: results include:
         assignedto_id
         comment
         created_by
         created_on
         custom_step_results []
         defects
         elapsed
         id
         status_id
         test_id
         version
        """
        rest_url = 'get_results/{0}'.format(test_id)
        if limit:
            rest_url += '&limit={0}'.format(limit)

        return self.get(rest_url)

    #
    # test_id =/= test_case_id
    #
    def get_test_result_test_case(self, test_run_id, test_case_id, limit=None):
        rest_url = 'get_results_for_case/{0}/{1}'.format(test_run_id, test_case_id)
        if limit:
            rest_url += '&limit={0}'.format(limit)

        try:
            return self.get(rest_url)
        except requests.HTTPError:
            PrintMessage("Failed getting data for test case: {0} from test run: {1}".format(test_case_id, test_run_id))

    def get_case_type_id_for_type(self, case_type):
        all_case_types = self.get_case_types()

        if case_type in [k['name'] for k in all_case_types]:
            return [k['id'] for k in self.get_case_types() if k['name'] == case_type][0]
        else:
            return None

    def get_field_value_id(self, field_name, field_value):
        """
        Retrieves automation type options. THis is case sensitive
        Processes response into a dictionary of types and ids
        :return: dictionary where key is type and value is field id
        """
        all_case_fields = self.get('get_case_fields')

        type_field = [k for k in all_case_fields if k['system_name'] == field_name][0]
        unclean_options = type_field['configs'][0]['options']['items'].split('\n')
        dict_field_options = {k.split(',')[1].strip(): k.split(',')[0] for k in unclean_options}

        return dict_field_options[field_value]

    def get_run_info(self, run_id):
        assert type(run_id) == int, 'Expected int value for the test run id.'

        rest_url = 'get_run/{0}'.format(run_id)

        return self.get(rest_url)

    def get_mile_stone_text(self, test_run_id):
        """
        Returns name of a mile stone if available, otherwise its empty value.
        :param test_run_id:
        :return:
        """
        run_info = self.get_run_info(test_run_id)

        if run_info['milestone_id'] is None:
            return ''

        mile_stone_url = 'get_milestone/{0}'.format(run_info['milestone_id'])

        return self.get(mile_stone_url)['name']

    def get_case_types(self):
        return self.get('get_case_types')

    def get_cases_by_id(self, project_id, suite_id, case_type, automation_type):
        """
        Retrieves test cases for given project id / suite id and case type
        Test cases are further filtered by expected automation type ids.
        This method strictly allows / removes test cases depending on given expected_automation_type_id
        :param project_id:
        :param suite_id:
        :param case_type:
        :param automation_type: (CommonCode/TestExecute/ExecuteEnums > AutomationType)

        if None: filter is not being applied and all tests are allowed through
        if Regression: only tests marked as regression are allowed through
        if Smoke: only tests marked as smoke are allowed through
        :return:
        """
        request_url = f'get_cases/{project_id}&suite_id={suite_id}&type_id={case_type}'
        all_cases = self.get(request_url)

        if automation_type and automation_type != AutomationTypeEnum.regression['name']:
            custom_automation_type_id = getattr(AutomationTypeEnum, automation_type)['id']
            return {k['id']: k for k in all_cases if custom_automation_type_id in k['custom_automation_type']}

        return {k['id']: k for k in all_cases}

    def get_sections(self, project_id, suite_id):
        """
        Returns a dictionary of sections driven by section id, rather than a list
        :param project_id:
        :param suite_id:
        :return:
        """
        request_url = 'get_sections/{0}&suite_id={1}'.format(project_id, suite_id)
        all_sections = self.get(request_url)
        return {k['id']: k for k in all_sections}

    def get_automation_type_options(self):
        """
        Retrieves automation type options
        Processes response into a dictionary of types and ids
        :return: dictionary where key is type and value is field id
        """
        # TODO: most likely unused - to remove.
        field_name = 'automation_type'
        all_case_fields = self.get('get_case_fields')

        automation_type_field = [k for k in all_case_fields if k['name'] == field_name][0]
        unclean_options = automation_type_field['configs'][0]['options']['items'].split('\n')

        return {k.split(',')[1].lower(): k.split(',')[0] for k in unclean_options}

    def get_cases_for_case_type(self, project_id, suite_id, automation_type=None):
        """
        Given case type is partially matched against test case types retrieved from test rail

        WMAP-7700 - Drive smoke testing execution via TestRail

        Logic is: if automation_type is specified and its other than regression, then execute only those tests.

        :param automation_type:
        :param suite_id: TestRail concept
        :param project_id: TestRail concept
        :return: Returns a dictionary by case_id
        """
        case_type = 'Automated'
        case_types = self.get('get_case_types')
        matched_case_type_id = [k['id'] for k in case_types if case_type in k['name']][0]

        return self.get_cases_by_id(project_id, suite_id, matched_case_type_id, automation_type)

    def add_section(self, project_id, suite_id, name, parent_id=None):
        post_url = f"add_section/{project_id}"
        body_request = {"suite_id": suite_id,
                        "name": name}
        if parent_id:
            body_request["parent_id"] = parent_id

        return self.post(post_url, body_request)

    def get_case(self, case_id):
        get_url = f"get_case/{case_id}"
        return self.get(get_url)

    def add_case(self, section_id, title, **kwargs):
        post_url = f"add_case/{section_id}"
        body_request = {'title': title}
        body_request.update(**kwargs)

        return self.post(post_url, body_request)

    def update_test_run_with_case_id(self, run_id, case_id):
        post_url = f"update_run/{run_id}"
        body_request = {'case_ids': [case_id]}

        return self.post(post_url, body_request)
