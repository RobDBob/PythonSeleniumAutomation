from collections import Counter

from CommonCode.Enums_Utils import TestResult
from CommonCode.TestExecute.Logging import PrintMessage
from CommonCode.TestExecute.TestContext import Test_Context
from CommonCode.TestReporting import Constants as Const
from CommonCode.TestReporting.MailClient import send_mail

test_status_to_result = {TestResult.Passed: 'Passed',
                         TestResult.Blocked: 'Blocked',
                         TestResult.Untested: 'Untested',
                         TestResult.Retest: 'Retest',
                         TestResult.Failed: 'Failed',
                         None: 'Untested'}


class ReportGenerator(object):
    def __init__(self, test_rail_client):
        self.test_rail = test_rail_client
        self.test_run = Test_Context.run_config.load('TestRun_Detail')

        self.all_sections = self.test_rail.get_sections(self.test_run['PROJECT_ID'], self.test_run['SUITE_ID'])
        self.all_cases = self.test_rail.get_cases_for_case_type(self.test_run['PROJECT_ID'],
                                                                self.test_run['SUITE_ID'])

        self.full_section_names = {}

    def _get_failed_test_results_with_history(self, all_tests_for_run):
        failed_tests = [k for k in all_tests_for_run if k['status_id'] == TestResult.Failed]

        expanded_failed_test_results = []
        for test_case in failed_tests:
            test_rail_results = self.test_rail.get_test_result(test_case['id'], limit=5)

            history = [k['status_id'] for k in test_rail_results]
            history.reverse()  # show results from most recent to oldest

            if test_rail_results:
                test_rail_results[0].update({'history': history})
                expanded_failed_test_results.append(test_rail_results[0])
            else:
                continue

        return expanded_failed_test_results

    @staticmethod
    def _get_test_result_history_color(test_history):
        entries = ''
        for result in test_history:
            if result == TestResult.Passed:
                color = '#0BC200'
            elif result == TestResult.Blocked:
                color = '#8c8c8c'
            elif result == TestResult.Failed:
                color = '#ff3300'
            else:
                color = '#f2f2f2'

            entries += Const.RESULT_HISTORY_ENTRY.format(color)

        return Const.RESULT_HISTORY.format(entries)

    @staticmethod
    def _get_result_and_color_from_status_code(status_code):
        if status_code == TestResult.Passed:
            color = '#33cc33'
        elif status_code == TestResult.Blocked:
            color = '#8c8c8c'
        elif status_code == TestResult.Failed:
            color = '#ff3300'
        else:
            color = '#f2f2f2'

        return test_status_to_result[status_code], color

    def _process_test_rail_results_into_sections(self, test_rail_results):
        """
        process test rails results into manageable data structure containing only details we're interested in
        """
        test_results_by_section = {}
        for test_rail_result in test_rail_results:
            test_result = {'test_id': 'C' + str(test_rail_result['case_id']),
                           'test_title': Const.TEST_TITLE.format(test_rail_result['id'],
                                                                 test_rail_result['title'])}

            test_pass_state, cell_color = self._get_result_and_color_from_status_code(test_rail_result['status_id'])
            test_result['test_pass_state'] = test_pass_state
            test_result['cell_color'] = cell_color

            full_section_name = self._get_full_section_name(test_rail_result['case_id'])

            if full_section_name not in test_results_by_section:
                test_results_by_section[full_section_name] = []
            test_results_by_section[full_section_name].append(test_result)

        return test_results_by_section

    def _build_full_section_name(self, section_id, child_title=''):
        section = self.all_sections[section_id]
        if child_title:
            new_title = "{0} - {1}".format(section['name'], child_title)
        else:
            new_title = section['name']

        if section['parent_id']:
            return self._build_full_section_name(section['parent_id'], new_title)
        else:
            return new_title

    def _get_full_section_name(self, case_id):
        try:
            section_id = self.all_cases[case_id]['section_id']
            if section_id not in self.full_section_names:
                new_section_title = self._build_full_section_name(section_id)
                self.full_section_names[section_id] = new_section_title

            return self.full_section_names[section_id]
        except KeyError:
            PrintMessage("Section not found for case id: {0}".format(case_id))

    def _update_results_table_with_all_tests(self, test_rail_results):
        test_results_by_section = self._process_test_rail_results_into_sections(test_rail_results)

        report_rows = []
        for full_section_name in test_results_by_section:
            report_rows.append(Const.ROW_TEMPLATE_SECTION.format(full_section_name))

            for test_result in test_results_by_section[full_section_name]:
                row = Const.ROW_TEMPLATE_ALL_RESULTS.format(test_result['test_id'],
                                                            test_result['test_title'],
                                                            test_result['cell_color'],
                                                            test_result['test_pass_state'])
                report_rows.append(row)

        return Const.TABLE_TEMPLATE_ALL_RESULTS.format(''.join(report_rows))

    def _update_results_table_with_failed_tests(self, all_tests_for_run):
        """
        Creates rows for table with failed results.
        This is one of the slowest methods as for each iteration it'll query TestRail for results
        This method executes longer the more failed results are present
        :param all_tests_for_run:
        :return:
        """
        report_rows = []
        for test in all_tests_for_run:
            if test['status_id'] != TestResult.Failed:
                continue

            test_result = self.test_rail.get_test_result(test['id'], limit=5)

            history = [k['status_id'] for k in test_result]
            history.reverse()  # show results from most recent to oldest

            test_result[0].update({'history': history})

            defects = test_result[0]['defects']

            row = Const.ROW_TEMPLATE_FAILURES.format('C' + str(test['case_id']),
                                                     Const.TEST_TITLE.format(test_result[0]['test_id'], test['title']),
                                                     Const.BUG_ID.format(defects) if defects else '',
                                                     test_result[0]['history'].count(TestResult.Failed),
                                                     self._get_test_result_history_color(test_result[0]['history']))
            report_rows.append(row)

        if len(report_rows) > 0:
            return Const.TABLE_TEMPLATE_FAILURES.format(''.join(report_rows),)
        else:
            return ''

    def _create_test_report_html_table(self, test_run_id, run_stats):
        result_types = [TestResult.Passed, TestResult.Failed]
        all_tests_for_run = self.test_rail.get_list_of_tests_for_run_id(test_run_id, status_id=result_types)

        PrintMessage("Test execution count: {0} in test run : {1}".format(len(all_tests_for_run), test_run_id))

        passed_table = self._update_results_table_with_all_tests(all_tests_for_run)
        failures_table = self._update_results_table_with_failed_tests(all_tests_for_run)

        return Const.REPORT_TEMPLATE.format(run_stats, failures_table, passed_table)

    @staticmethod
    def _format_time_taken(time_taken):
        hours = int(time_taken / 3600)
        minutes = int((time_taken - (hours * 3600))/60)

        formatted_message = Const.TIME_TAKEN.format(hours, minutes)
        PrintMessage('TimeTaken: {0}'.format(formatted_message))
        return formatted_message

    def _get_build_number(self, test_run_id):
        """
        Retrieves most common build number from last few test executions
        :param test_run_id:
        :return:
        """
        test_case_count = len(self.all_cases)
        build_numbers = [k['version'] for k in self.test_rail.get_results_for_run(test_run_id, limit=3*test_case_count)]

        PrintMessage("Found build numbers in test results: {0}".format(build_numbers))

        return Counter(build_numbers).most_common()[0][0]

    def generate_and_send(self, recipients, build_number, time_taken):
        if not recipients:
            PrintMessage("No report recipients supplied - SKIPPING SENDING REPORT")
            return

        test_run_id = self.test_run['RUN_ID']
        run_info = self.test_rail.get_run_info(test_run_id)
        passed_count = run_info['passed_count']
        failed_count = run_info['failed_count']
        blocked_count = run_info['blocked_count']

        total_pass_count = passed_count + run_info['custom_status1_count']
        total_count_ex_blocked = total_pass_count + failed_count

        pass_rate = round(float(total_pass_count) / total_count_ex_blocked * 100, 2)

        run_stats = Const.STATS_TEMPLATE.format(total_pass_count + failed_count + blocked_count,
                                                passed_count,
                                                failed_count,
                                                blocked_count,
                                                passed_count + failed_count,
                                                pass_rate,
                                                self._format_time_taken(time_taken),
                                                Test_Context.report_hyper_link)

        test_report = self._create_test_report_html_table(test_run_id, run_stats)

        report_build_number = build_number if build_number else self._get_build_number(test_run_id)

        mail_title = Const.EMAIL_TITLE.format(run_info['name'],
                                              pass_rate,
                                              total_pass_count,
                                              total_count_ex_blocked,
                                              self.test_rail.get_mile_stone_text(test_run_id),
                                              report_build_number)

        send_mail(mail_title,
                  test_report,
                  self.test_run['REPORT_SENDER'],
                  recipients)
