import platform
import sys

from CommonCode.TestExecute.Logging import PrintMessage


def print_used_library_versions():
    PrintMessage(f"Python version: {platform.python_version()}")
    PrintMessage(f"Sys version: {sys.version_info}")
