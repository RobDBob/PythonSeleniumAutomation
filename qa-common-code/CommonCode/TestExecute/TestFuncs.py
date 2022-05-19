class ResultUpdater(object):
    @staticmethod
    def _process_test_results(failed, failed_re_run):
        """

        :param failed: results of a whole run
        :param failed_re_run: results of re_run
        :return:
        """
        failed_re_run_method_names = [k[0]._testMethodName for k in failed_re_run]
        second_try_pass_indexes = []
        for index in range(len(failed)):
            if failed[index][0]._testMethodName in failed_re_run_method_names:
                continue
            else:
                second_try_pass_indexes.append(index)

        second_try_pass_indexes.reverse()
        for index in second_try_pass_indexes:
            failed.pop(index)

    @staticmethod
    def update_results_with_re_run(results, re_rerun_results):
        """

        :param results: results of a whole run
        :param re_rerun_results: results of re_run
        :return:
        """
        ResultUpdater._process_test_results(results.failures, re_rerun_results.failures)
        ResultUpdater._process_test_results(results.errors, re_rerun_results.errors)


def get_re_run_test_ids(prev_result):
    all_failed = prev_result.failures + prev_result.errors
    return [test_id_from_test_name(k[0]._testMethodName, True) for k in all_failed]


def test_id_from_test_name(test_name, make_int=False):
    """
    Method extracts test id from test name i.e. test_C1234_test_method_at_the_finest -> 1234
    :param test_name:
    :param make_int:
    :return:
    """
    if make_int:
        return int(test_name.split('_')[1].replace('C', ''))
    return test_name.split('_')[1].replace('C', '')


def iterate_tests(test_suite_or_case):
    """Iterate through all of the test cases in 'test_suite_or_case'."""
    try:
        suite = iter(test_suite_or_case)
    except TypeError:
        yield test_suite_or_case
    else:
        for test in suite:
            for subtest in iterate_tests(test):
                yield subtest
