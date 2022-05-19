import logging
import os
import sys
from datetime import datetime
from time import strftime

from CommonCode.Enums_Utils import LoggingLevel
from CommonCode.TestExecute.TestContext import Test_Context
from CommonCode.TestHelpers.StringMethods import get_unique_name

uniqueId = strftime('%d_%H%M%S')
PREFIXED_MESSAGE_FORMAT = "{0}: {1} {2}"
MESSAGE_FORMAT = "{0} {1}"


def PrintMessage(message, level=LoggingLevel.info):
    time_stamp = datetime.now().strftime("%d-%b-%Y %H:%M:%S.%f")[:-4]

    logger = logging.getLogger(Test_Context.log_name)
    if level == LoggingLevel.error:
        logger.info(PREFIXED_MESSAGE_FORMAT.format(LoggingLevel.error.upper(), time_stamp, message))
    elif level == LoggingLevel.warning:
        logger.info(PREFIXED_MESSAGE_FORMAT.format(LoggingLevel.warning.upper(), time_stamp, message))
    elif level == LoggingLevel.debug and Test_Context.run_debug:
        logger.info(PREFIXED_MESSAGE_FORMAT.format(LoggingLevel.debug.upper(), time_stamp, message))
    elif level == LoggingLevel.info:
        logger.info(MESSAGE_FORMAT.format(time_stamp, message))


class StreamToLogger(object):
    def __init__(self, log_name, log_folder):
        log_file_path = os.path.join(log_folder, f"testRunDiary_{uniqueId}_{get_unique_name(prefix='')}.log")
        self.log_file_handler = open(log_file_path, 'w', encoding="utf-8")
        self.log_name = log_name

        self.datetime_stamp = strftime('%b%d_%H%M')
        self.terminal = sys.stdout
        self._set_test_log()

    def __del__(self):
        self.log_file_handler.close()

    def _set_test_log(self):
        logger = logging.getLogger(self.log_name)
        logger.setLevel(logging.INFO)
        logger.addHandler(logging.StreamHandler(self))

    def write(self, buf):
        if not buf.lower().startswith(LoggingLevel.debug):
            self.terminal.write(buf)
        self.log_file_handler.write(buf)

    def flush(self):
        self.terminal.flush()
        self.log_file_handler.flush()
