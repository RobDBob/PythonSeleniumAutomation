# noinspection PyDeprecation
import imp
import inspect
import os
import sys
import unittest

from CommonCode.TestExecute.Logging import PrintMessage


class TestDiscoverySingleTestRun(unittest.TextTestRunner):
    """
    Class used in searching test folders. This is a supplement to unittest as it works of test ids and test class names
    """
    @staticmethod
    def _get_list_of_test_files(test_files_path, test_type):
        """
        the type is used to get correct files (either RegressionSuite or SmokeSuite)
        :param test_files_path:
        :param test_type:
        :return:
        """
        def filter_fun(x): return 'pyc' not in x and '__init__' not in x and '.orig' not in x and test_type in x
        tests_files = os.listdir(test_files_path)
        return list(filter(filter_fun, tests_files))

    # returns list of classes
    # the type is used to get correct files (either RegressionSuite or SmokeSuite)
    # returns list of pairs: 'name_of_class', actual class; the latter is used in test execution

    def get_test_classes(self, with_file_name):
        test_files_path = os.getcwd() + '/Tests'

        test_files = self._get_list_of_test_files(test_files_path, with_file_name)
        test_classes = []
        for test_files_with_ext in test_files:
            module_name = test_files_with_ext.rstrip('.py')
            path_to_file = test_files_path + '/' + test_files_with_ext

            # noinspection PyDeprecation
            imp.load_source(module_name, path_to_file)
            module_members = inspect.getmembers(sys.modules[module_name], inspect.isclass)
            test_classes += [k for k in module_members if module_name in k[1].__module__]

        return test_classes

    @staticmethod
    def _get_test_id(test_method_name):
        test_id = ''
        try:
            test_id = int(test_method_name.split('_')[1].replace('C', ''))
        finally:
            return test_id

    def get_suite_from_test_ids(self, test_ids):
        """
        To preserve order of test ids, firstly we need to iterate through classes
        :param test_ids:
        :return:
        """
        all_test_classes = self.get_test_classes('Tests')

        found_test_with_class = {}
        found_test_count = 0
        for test_class in all_test_classes:
            all_class_methods = list(test_class[1].__dict__.keys())

            test_methods = [test_method for test_method in all_class_methods if 'test_C' in test_method]
            matched_tests = [matched for matched in test_methods if self._get_test_id(matched) in test_ids]

            for test in matched_tests:
                found_test_with_class.update({test: test_class[1]})
            found_test_count += len(matched_tests)

            # breaking out when found all expected tests
            if found_test_count == len(test_ids):
                break

        suite = unittest.TestSuite()

        if len(found_test_with_class) == 0:
            PrintMessage('Failed to find test with id: {0}'.format(test_ids))
            return suite

        # to preserve order in which tests were specified, adding tests as they were initially put in
        for test_id in test_ids:
            indices = [i for i, s in enumerate(found_test_with_class.keys()) if str(test_id) in s]
            if len(indices) > 0:
                index = indices[0]
            else:
                PrintMessage("Failed to find test with test id: {0}".format(test_id))
                continue

            test_name = list(found_test_with_class.keys())[index]
            class_name = found_test_with_class[test_name]

            suite.addTest(class_name(test_name))

        return suite

    def get_suite_from_test_class(self, classes_to_run):
        all_classes = self.get_test_classes('Tests')

        def match(class_x, class_bunch): return[x for x in class_bunch if class_x.lower() in x[0].lower()]

        all_found = []
        for class_to_run in classes_to_run:
            found = match(class_to_run, all_classes)
            if not found:
                PrintMessage("Not found class name: {0}".format(class_to_run))
                continue

            all_found += found

        suite = unittest.TestSuite()
        loader = unittest.TestLoader()

        if len(all_found) == 0:
            PrintMessage('Failed to find test class with class(s) name: {0}'.format(classes_to_run))
            return suite

        all_found = list(set(all_found))  # casting to set and back to list removes any duplicates

        for class_found in all_found:
            PrintMessage("Executing tests from test class: {0}".format(class_found[0]))
            suite.addTests(loader.loadTestsFromTestCase(class_found[1]))

        return suite

    def get_suite_with_attribute(self, attribute_name):
        """
        Add all tests to suite where attribute name is present.
        The attribute name is decorator name i.e smoke
        :param attribute_name:
        :return:
        """
        all_test_classes = self.get_test_classes('Tests')

        suite = unittest.TestSuite()
        for test_class in all_test_classes:
            test_pair = test_class[1].__dict__

            test_methods = [test_method for test_method in list(test_pair.keys()) if 'test_C' in test_method]
            matched_tests = [m for m in test_methods if getattr(test_pair[m], attribute_name, False)]

            for test_name in matched_tests:
                suite.addTest(test_class[1](test_name))

        return suite
