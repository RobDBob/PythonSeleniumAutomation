import traceback

from CommonCode.TestExecute.Logging import PrintMessage


def try_execute(method, *args, **kwargs):
    try:
        return method(*args, **kwargs)
    except Exception as e:
        tb = traceback.format_exc()
        PrintMessage('Encountered exception {0}, with args {1}'.format(type(e), e.args))
        PrintMessage(str(e))
        PrintMessage("traceback: {0}".format(tb))
        pass
