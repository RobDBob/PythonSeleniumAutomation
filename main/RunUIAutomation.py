#!/usr/bin/env
import multiprocessing
import time
import os
import subprocess
from contextlib import contextmanager

import paramiko
from CommonCode import ZipTools
from CommonCode.TestExecute.CommandLineArgumentsParser import CommandLineArgumentsParser
from CommonCode.TestExecute.RunManager import RunManager
from CommonCode.TestExecute.TestContext import Test_Context


@contextmanager
def poolcontext(*args, **kwargs):
    """
    Pool context
    :param args:
    :param kwargs:
    :return:
    """
    if Test_Context.browser_stack:
        processes_count = 5
    else:
        # Make the adjustment only if we're running against THE BEAST, i.e. more than 12 cores
        available_cores = multiprocessing.cpu_count()
        processes_count = available_cores - 2 if available_cores > 12 else None

    pool = multiprocessing.Pool(processes=processes_count, *args, **kwargs)
    yield pool
    pool.terminate()


def upload_stuff(env, build_number):
    files_to_copy = ['test_logs.zip', 'screenshots.zip']

    # noinspection PyTypeChecker
    transport = paramiko.Transport(('10.89.170.236', 22))
    transport.connect(username='sftp', password='sftp')

    sftp = paramiko.SFTPClient.from_transport(transport)

    try:
        folder_name = f"logs_{env}_build_{build_number}"
        sftp.mkdir(folder_name)

        for file_to_copy in files_to_copy:
            sftp.put(file_to_copy, os.path.join(folder_name, file_to_copy))
    finally:
        sftp.close()


def start_browserstack_session():
    if not Test_Context.browser_stack:
        return

    browserstack_details = Test_Context.run_config.load('BrowserStackDetails')
    DETACHED_PROCESS = 0x00000008
    subprocess.Popen(["BrowserStackLocal", "--key", browserstack_details["ACCESS_KEY"], "--force-local"],
                     shell=True,
                     stdin=None,
                     stdout=None,
                     stderr=None,
                     close_fds=True,
                     creationflags=DETACHED_PROCESS)

    # establishing connection takes time and there is no obvious way to communicate success up, so we blindly wait
    time.sleep(3)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    parsed_args = CommandLineArgumentsParser.process_arguments_group_test_run()

    with RunManager(parsed_args) as test_runner:
        start_browserstack_session()
        test_runner.run_bunch(custom_pool_context=poolcontext,
                              path_to_users_file="./ConfigFiles/TestUsers.json",
                              post_execution_cb=[ZipTools.zip_test_logs_cb,
                                                 ZipTools.zip_screenshots_cb])

    # temp code as a replacement for magic_repo functionality while jenkins is being fixed
    from CommonCode.HelperFunctions import try_execute

    try_execute(upload_stuff, parsed_args.current_config_file_name, parsed_args.build_number)
