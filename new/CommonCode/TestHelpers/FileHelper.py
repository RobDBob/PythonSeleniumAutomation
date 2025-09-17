import os
from retry import retry
from CommonCode.CustomExceptions import FileNotReadyException
from CommonCode.TestExecute.Logging import PrintMessage


@retry(exceptions=FileNotReadyException, delay=2, tries=5)
def waitForFileToBeRemoved(filePath):
    if os.path.isfile(filePath):
        raise FileNotReadyException("File still present")


@retry(exceptions=FileNotReadyException, delay=10, tries=5)
def waitForNewFile(existingFiles, downloadFolder):
    currentFiles = os.listdir(downloadFolder)
    PrintMessage(f"Current files: {currentFiles}")
    if len(currentFiles) == len(existingFiles):
        raise FileNotReadyException("File not downloaded yet")
    if [k for k in currentFiles if "crdownload" in k]:
        raise FileNotReadyException("File still downloading")

    diff = list(set(currentFiles) - set(existingFiles))
    if diff:
        return [os.path.join(downloadFolder, k) for k in diff][0]
    return None
