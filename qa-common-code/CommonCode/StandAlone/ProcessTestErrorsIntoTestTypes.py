#!/usr/bin/env python

import argparse
import os


class ProcessTestErrorsIntoTestTypes(object):
    text_start_fail_section = "======================================================================"
    text_assert_border = "----------------------------------------------------------------------"

    def __init__(self):
        self.error_types = dict()

    def _update_error_types(self, error_type, test_name):
        if error_type not in self.error_types:
            self.error_types[error_type] = [test_name]
        else:
            self.error_types[error_type].append(test_name)

    @staticmethod
    def _indices_in(list_struct, search_term):
        return [idx for idx, k in enumerate(list_struct) if search_term in k]

    def _indices_assert_borders(self, list_struct, search_term, start=0, end=-1):
        if start is None:
            return None

        list_struct_sub = list_struct[start:end]
        indexes = self._indices_in(list_struct_sub, search_term)
        return (start + indexes[0], start + indexes[1]) if len(indexes) > 1 else (None, None)

    @staticmethod
    def _get_error_type_value(text_slice):
        for sub_set in text_slice:
            if 'error' in sub_set.lower() or 'exception' in sub_set.lower():
                return sub_set

    def _process_single_test_failure(self, file_content, start_index):
        assert_start_index, assert_end_index = self._indices_assert_borders(file_content,
                                                                            self.text_assert_border,
                                                                            start=start_index)

        error_type = self._get_error_type_value(file_content[assert_start_index:assert_end_index])
        test_name = file_content[start_index:assert_start_index][1]
        self._update_error_types(error_type, test_name)

    def _process_file(self, file_path):
        with open(file_path, "r") as file_object:
            file_content = file_object.readlines()
            failed_test_section_indices = self._indices_in(file_content, self.text_start_fail_section)
            for start_index in failed_test_section_indices:
                self._process_single_test_failure(file_content, start_index)

    def _write_output_file(self, output_file_name):
        with open(output_file_name, 'w') as output:
            for error_type in sorted(self.error_types):
                output.write("TYPE: {0}".format(error_type))
                output.writelines(self.error_types[error_type])
                output.write("\n\r")

    def process_test_errors_into_test_types(self, test_logs_path):
        """
        Class public method.
        Takes path to log files. Open each log file in a sequence and processess its contents.
        Results are written to output file.
        :param test_logs_path:
        :return:
        """
        file_list = os.listdir(test_logs_path)
        output_file_name = 'output.txt'

        for file_name in file_list:
            if 'testRunDiary' not in file_name:
                continue
            self._process_file(os.path.join(test_logs_path, file_name))

        self._write_output_file(output_file_name)

        return os.path.join(os.getcwd(), output_file_name)


def configure_arg_parse():
    help_text = "Specify folder where log files are located. Expecting testRunDiary*.log files"
    parser = argparse.ArgumentParser(prefix_chars='-')
    parser.add_argument('-f',
                        dest='folder_path',
                        help=help_text,
                        required=True)
    return parser.parse_args()


if __name__ == "__main__":
    parse_args = configure_arg_parse()
    folder_path = parse_args.folder_path

    assert os.path.isdir(folder_path)

    test_log_processor = ProcessTestErrorsIntoTestTypes()
    test_log_processor.process_test_errors_into_test_types(folder_path)
