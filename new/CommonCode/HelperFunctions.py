import traceback
import re


def tryExecute(method, *args, **kwargs):
    from CommonCode.TestExecute.Logging import PrintMessage
    try:
        return method(*args, **kwargs)
    except Exception as e:
        tb = traceback.format_exc()
        PrintMessage(f"Encountered exception {type(e)}, with args {e.args}")
        PrintMessage(str(e))
        PrintMessage(f"traceback: {tb}")
    return


def getTestIdFromTestName(testName):
    from CommonCode.TestExecute.Logging import PrintMessage
    try:
        return int(re.search(r'C(\d+)', testName).group(1))
    except AttributeError:
        PrintMessage(f"Failed processing test {testName}, id failed to extract")
        return None
    

def instanceDir(obj):
    """
    Same as dir with exception, it'll ignore internal variables
    :param obj:
    :return:
    """
    return [k for k in dir(obj) if not k.startswith('__') and getattr(type(obj), k, None) in [False, True, None]]
