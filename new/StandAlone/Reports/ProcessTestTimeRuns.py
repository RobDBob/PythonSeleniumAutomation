import argparse
import os
import re
from time import gmtime, mktime, strftime, strptime
from CommonCode.TestExecute import Constants as Const


class ProcessTestTimeRuns:
    START_TEST_SECTION = ">>>>>> Test in progress: test_C"
    DATE_TIME_REG = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})"
    DATE_TIME_FORMAT = r"%Y-%m-%d %H:%M:%S,%f"

    OUTPUT_FILE_NAME = "LogProcessing_TestRunTimes.txt"

    def __init__(self, folderPath):
        self.folderPath = folderPath
        self.testDurationInSecs: dict = {}

    @staticmethod
    def _indicesIn(listStruct, searchTerm):
        return [idx for idx, k in enumerate(listStruct) if searchTerm in k]

    def _getEndTestLogIndex(self, fileContent, startSectionIndex):
        endSectionIndex = self._indicesIn(fileContent[startSectionIndex:], Const.TEST_TAIL)
        if endSectionIndex:
            return endSectionIndex[0] + startSectionIndex
        return -1

    def _getTimeObjFromIndex(self, fileContent, contentIndex):
        """
        if contentIndex points to the start of test
        move two lines to first entry with date stamp:

        >>>>>> Test in progress: test_C1459160_VerifyTrustServicingRemoveCorporateTrusteePreAccountCreation
        >>>>>>
        2025-09-04 19:59:22,576 - TestsRemoveCorporateTrustee:70 - INFO - Browser Setup > HEADLESS > Using chrome
        """

        textToProcess = fileContent[contentIndex + 2] if "Test in progress" in fileContent[contentIndex] else fileContent[contentIndex]
        matchObj = re.search(ProcessTestTimeRuns.DATE_TIME_REG, textToProcess)
        if matchObj:
            return strptime(matchObj[0], ProcessTestTimeRuns.DATE_TIME_FORMAT)
        return None

    def _processFile(self, filePath):
        with open(filePath, "r", encoding="utf-8") as fp:
            fileContent = [line.rstrip("\n") for line in fp.readlines()]
            startTestSectionIndices = self._indicesIn(fileContent, self.START_TEST_SECTION)
            for startSectionIndex in startTestSectionIndices:
                matchObj = re.search("test_C(.*)", fileContent[startSectionIndex])
                if not matchObj:
                    print("error, no test found")
                    continue

                testName = matchObj.group(0)
                endSectionIndex = self._getEndTestLogIndex(fileContent, startSectionIndex)

                startTimeStamp = self._getTimeObjFromIndex(fileContent, startSectionIndex)
                endTimeStamp = self._getTimeObjFromIndex(fileContent, endSectionIndex)

                self.testDurationInSecs[testName] = mktime(endTimeStamp) - mktime(startTimeStamp)

    def _writeOutputFile(self):
        outputFilePath = os.path.join(self.folderPath, self.OUTPUT_FILE_NAME)
        sortedTestDurationInSecs = sorted(self.testDurationInSecs.items(), key=lambda item: -item[1])
        with open(outputFilePath, "w", encoding="utf-8") as output:
            for dataPair in sortedTestDurationInSecs:
                formatedDuration = strftime('%H:%M:%S', gmtime(dataPair[1]))
                output.write(f"{formatedDuration} {dataPair[0]}\n")

    def _writeOutputToConsole(self):
        sortedTestDurationInSecs = sorted(self.testDurationInSecs.items(), key=lambda item: -item[1])
        for dataPair in sortedTestDurationInSecs:
            formatedDuration = strftime('%H:%M:%S', gmtime(dataPair[1]))
            print(f"{formatedDuration} {dataPair[0]}")

    def processTestRunTimes(self):
        fileList = os.listdir(self.folderPath)

        for fileName in fileList:
            if "main" in fileName or "Tests" not in fileName:
                continue
            self._processFile(os.path.join(self.folderPath, fileName))

        self._writeOutputFile()
        self._writeOutputToConsole()


def configureArgParse():
    helpText = "Specify folder where log files are located. Expecting testRunDiary*.log files"
    parser = argparse.ArgumentParser(prefix_chars='-')
    parser.add_argument('-f',
                        dest='folderPath',
                        help=helpText,
                        required=True)
    return parser.parse_args()


if __name__ == "__main__":
    parse_args = configureArgParse()
    folderPath = parse_args.folderPath

    assert os.path.isdir(folderPath)

    test_log_processor = ProcessTestTimeRuns(folderPath)
    test_log_processor.processTestRunTimes()
