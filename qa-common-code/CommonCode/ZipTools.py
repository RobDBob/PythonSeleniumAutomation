import csv
import os
import zipfile

from CommonCode.HelperFunctions import try_execute
from CommonCode.StandAlone.ProcessTestErrorsIntoTestTypes import ProcessTestErrorsIntoTestTypes
from CommonCode.TestExecute.Logging import PrintMessage


def get_csv_content_of_zip_file(zip_file_path):
    assert zipfile.is_zipfile(zip_file_path), f"Expected {zip_file_path} to be zip file"

    with zipfile.ZipFile(zip_file_path) as myzip:
        assert len(myzip.filelist) > 0, 'Expected at least one csv file'

        with myzip.open(myzip.filelist[0].filename) as my_csv_file:
            csv_file_content = my_csv_file.read()

            # decode and clean up string,
            csv_file_content = csv_file_content.decode(encoding='utf-8')
            csv_file_content = csv_file_content.split('\n')
            return csv.DictReader(csv_file_content)


def zip_files_in_folder(zip_file_path, files_to_zip):
    PrintMessage(f"Zipping {len(files_to_zip)}-files to folder {zip_file_path}")
    with zipfile.ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED) as myzip:
        for file_to_zip in files_to_zip:
            myzip.write(file_to_zip)


def zip_test_logs_cb(test_context):
    """
    Process test logs to get useful stats as:
    - Failed tests grouped by test failure
    - Test duration for each test (excluding setup & browser refresh)
    :return:
    """
    log_folder = test_context.get_required_folder('logging')
    if log_folder is None or os.listdir(log_folder) == []:
        PrintMessage("No logs to zip, skipping.")
        return

    log_files_to_zip = [os.path.join(log_folder, log_file) for log_file in os.listdir(log_folder)]

    test_summary_file_path = try_execute(ProcessTestErrorsIntoTestTypes().process_test_errors_into_test_types, log_folder)
    if test_summary_file_path:
        log_files_to_zip.append(test_summary_file_path)

    zip_files_in_folder(os.path.join(os.getcwd(), 'test_logs.zip'), log_files_to_zip)


def zip_screenshots_cb(test_context):
    screenshots_folder = test_context.get_required_folder('screenshots')
    if screenshots_folder is None or os.listdir(screenshots_folder) == []:
        PrintMessage("No screenshots to zip, skipping.")
        return

    screenshots_to_zip = [os.path.join(screenshots_folder, log_file) for log_file in os.listdir(screenshots_folder)]
    zip_files_in_folder(os.path.join(os.getcwd(), 'screenshots.zip'), screenshots_to_zip)

    PrintMessage(f'Zip files created!')


def zip_test_results_cb(test_context):
    test_results_folder = test_context.get_required_folder('results')
    if test_results_folder is None or os.listdir(test_results_folder) == []:
        PrintMessage("No test results to zip, skipping.")
        return

    zip_file_path = os.path.join(os.path.curdir, 'test_results.zip')
    files_to_zip = [os.path.join(test_results_folder, file_name) for file_name in os.listdir(test_results_folder)]

    zip_files_in_folder(zip_file_path, files_to_zip)
