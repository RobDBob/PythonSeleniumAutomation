import inspect
import logging
import os
from CommonCode.TestExecute.TestContext import Test_Context


def getTestFrame():
    """
    Reads through call stack to find frame from test level if succeeds, its returned
    Otherwise pre-logging frame is returned
    """
    initialFrame = inspect.currentframe().f_back

    frame = initialFrame.f_back
    frames = []
    while frame.f_back is not None:
        frames.append(frame)
        frame = frame.f_back

    testFrames = [k for k in frames if os.path.basename(k.f_code.co_filename).startswith("Tests")]
    if testFrames:
        return testFrames[0]
    return initialFrame


# pylint: disable=invalid-name
def PrintMessage(message, level=logging.INFO, inStepMessage=False):
    """
    Inner adds indendation
    """
    logger = getLogger(level)
    message = message if not inStepMessage else f"{' '*4}{message}"
    logger.log(level, message)


def configureLogger(logger, loggingFilePath):
    logging.setLogRecordFactory(recordFactory)

    formatter = logging.Formatter("%(asctime)s - %(name)s:%(lineNo)s - %(levelname)s - %(message)s")

    logFileHandler = logging.FileHandler(loggingFilePath, 'a+', encoding='utf-8', errors=None)
    logFileHandler.setFormatter(formatter)
    logFileHandler.setLevel(logging.NOTSET)
    logger.addHandler(logFileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    consoleHandler.setLevel(logging.INFO)
    logger.addHandler(consoleHandler)


def getLogger(level=logging.DEBUG):
    if Test_Context.currentTestClassName:
        loggerName = Test_Context.currentTestClassName
    else:
        loggerName = "main"

    logger = logging.getLogger(loggerName)
    logger.level = level

    if not logger.handlers:
        os.makedirs(Test_Context.getRequiredFolders("logging"), exist_ok=True)
        loggingFilePath = os.path.join(Test_Context.getRequiredFolders("logging"), f"{logger.name}.log")
        configureLogger(logger, loggingFilePath)
    return logger


oldRecordFactory = logging.getLogRecordFactory()


def recordFactory(*args, **kwargs):
    currFrame = getTestFrame()
    record = oldRecordFactory(*args, **kwargs)
    record.lineNo = currFrame.f_lineno
    return record
