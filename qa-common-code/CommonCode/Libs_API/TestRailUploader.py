import re
from unittest.case import _SubTest

from CommonCode.Enums_Utils import TestResult
from CommonCode.Libs_API.APIClient_TestRail import TestRailAPIClient
from CommonCode.TestExecute import TestFuncs
from CommonCode.TestExecute.Logging import PrintMessage


class TestRailResultUploader(object):
    """
    Converts UnitTest results to format accepted by Test Rail
    Uploads test results to Test Rail
    """
    def __init__(self, main_test_context, test_suite):
        self.tested_build_version = main_test_context.build_number
        self.test_suite = test_suite
        self.test_run_id = main_test_context.run_config.load('TestRun_Detail')['RUN_ID']

        test_rail_info = main_test_context.test_rail_config
        self.test_rail = TestRailAPIClient(
            test_rail_info['URL'],
            test_rail_info['User'],
            test_rail_info['Password'])

        self.tests_in_run = self.test_rail.get_list_of_tests_for_run_id(self.test_run_id)

        self._parent_test_section_id = {}
        self.new_case_fields = self._get_new_case_fields()

    def _get_new_case_fields(self):
        return {'custom_review_status': self.test_rail.get_field_value_id('custom_review_status',
                                                                          'Review Pending'),
                'custom_automation_type': [self.test_rail.get_field_value_id('custom_automation_type',
                                                                             'Regression')],
                'type_id': self.test_rail.get_case_type_id_for_type('Automated')}

    def _get_case_id_if_test_exists_in_test_rail(self, test_name):
        """
        This is only used in context of sub-tests.
        This method uses test case title as a form of identification vs TestRail.
        If test with specific title is not found then new test is created with that title and used forward.
        :param test_name:
        :return:
        """
        test_titles = [k['title'] for k in self.tests_in_run]
        if test_name in test_titles:
            index = test_titles.index(test_name)
            return self.tests_in_run[index]['case_id']
        else:
            return 0

    def _parent_test_case_section_id(self, parent_case_id):
        """
        Returns id section for 'dynamic tests' or creates new section in test suite
        :return:
        """
        if parent_case_id not in self._parent_test_section_id:
            parent_test_case = self.test_rail.get_case(parent_case_id)
            self._parent_test_section_id[parent_case_id] = parent_test_case['section_id']

        return self._parent_test_section_id[parent_case_id]

    def _create_new_test(self, test_name, parent_case_id):
        section_id = self._parent_test_case_section_id(parent_case_id)
        result = self.test_rail.add_case(section_id, test_name, **self.new_case_fields)
        self.test_rail.update_test_run_with_case_id(self.test_run_id, result['id'])

        return result['id']

    def _get_test_id_from_subtest(self, test_case):
        """
        This method assumes subtests used in execution have two TWO parameters, two table names
        TODO: For use in other frameworks going forward -
              this method need to be standardized or overridden in each framework.
        :param test_case:
        :return:
        """
        test_name = list(test_case.params.maps[0].values())[0]

        case_id = self._get_case_id_if_test_exists_in_test_rail(test_name)
        if case_id:
            return case_id
        else:
            parent_case_id = TestFuncs.test_id_from_test_name(test_case.test_case._testMethodName)
            return self._create_new_test(test_name, parent_case_id)

    def _get_test_case_id_out(self, test_case):
        if isinstance(test_case, _SubTest):
            return self._get_test_id_from_subtest(test_case)
        else:
            # TODO: to update when this gets merged to Common, no need for test name and test class data.
            test_name, test_case_id, class_name = self._get_test_details(str(test_case))
            return test_case_id

    # formatting: test_C26315_UDP_Fragments_Bit (__main__.Test_RuleChecking) into something more usable
    @staticmethod
    def _get_test_details(test_full_name):
        test_name = test_id = class_name = None
        try:
            test_full_name = str(test_full_name)
            test_name, module_name = test_full_name.split(' ')
            test_id = TestFuncs.test_id_from_test_name(test_name)
            file_name, class_name = module_name.strip('()').split('.')

            return test_name, test_id, class_name

        except:
            PrintMessage("_get_test_details > failed parsing test with name: {0}".format(test_full_name))

        return test_name, test_id, class_name

    # get last 7 results from the test
    # results are ordered from most recent to oldest
    # returns [latest_defect, fail_count]
    def _get_most_recent_defect_id(self, test_case_id, limit=7):
        test_results = self.test_rail.get_test_result_test_case(self.test_run_id,
                                                                test_case_id,
                                                                limit)
        if test_results:
            for test_result in test_results:
                if test_result['status_id'] == TestResult.Passed:
                    return ''
                if test_result['defects']:
                    return test_result['defects']

        return ''

    def _process_failed_class(self, failed_class, test_status):
        """
        Addresses issue from WMAP-5535
        :return:
        :param failed_class: i.e. 'setUpClass (TestsRestAPIBulkDownload.RegressionAPIBulkDownloadsTests)'
        """
        description_with_class_name = failed_class[0].description
        class_name = re.search(r'\.(\w*)\)', description_with_class_name).group(1)
        all_class_tests = [k for k in self.test_suite._tests if type(k).__name__ == class_name]

        failed_tests_results = dict()
        for test in all_class_tests:
            failed_tests_results.update(self._process_failed_test(str(test), failed_class[1], test_status))

        return failed_tests_results

    def _process_failed_test(self, test_case, test_comment, test_status):
        test_case_id = self._get_test_case_id_out(test_case)

        # if failed to get the test_case_id, skip
        # the exception will be logged in _get_test_details method
        if test_case_id is None:
            return {}

        latest_defect = self._get_most_recent_defect_id(test_case_id)

        return {test_case_id: [test_status, test_comment, latest_defect]}

    def _process_passed_tests(self, passed_tests):
        passed_tests_results = dict()
        for test_case in passed_tests:
            test_case_id = self._get_test_case_id_out(test_case)

            if test_case_id is None:
                return {}

            passed_tests_results.update({test_case_id: [TestResult.Passed, 'Thumbs Up', '']})

        return passed_tests_results

    def _process_failed_tests(self, failed_tests, test_status):
        """
        processes failed, errored and skipped tests
        :param failed_tests:
        :param test_status:
        :return:
        """
        if len(failed_tests) == 0:
            return dict()

        failed_tests_results = dict()
        for failed_test in failed_tests:
            if hasattr(failed_test[0], 'description') and 'setUpClass' in failed_test[0].description:
                processed_failed_tests = self._process_failed_class(failed_test, test_status)
            else:
                processed_failed_tests = self._process_failed_test(failed_test[0],
                                                                   str(failed_test[1]),
                                                                   test_status)

            failed_tests_results.update(processed_failed_tests)
        return failed_tests_results

    def process_and_upload(self, test_results):
        test_results_processed = dict()

        # Processing 4 lists of results obtained from unittest [failures, errors, skipped, passed]
        test_results_processed.update(self._process_failed_tests(test_results.failures, TestResult.Failed))
        test_results_processed.update(self._process_failed_tests(test_results.errors, TestResult.Failed))
        test_results_processed.update(self._process_failed_tests(test_results.skipped, TestResult.Blocked))
        test_results_processed.update(self._process_passed_tests(test_results.passed))

        self.test_rail.post_test_results(self.tested_build_version, self.test_run_id, test_results_processed)
