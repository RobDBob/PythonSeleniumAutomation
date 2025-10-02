import argparse
import os
import re


class ProcessTestErrorsIntoTestTypes:
    START_FAIL_SECTION = "------------ Error log START for: "
    END_FAIL_SECTION = "------------ Error log END for: "

    OUTPUT_FILE_NAME = "LogProcessing_CommonErrors.txt"

    def __init__(self, folderPath):
        self.folderPath = folderPath
        self.errorTypes: list[dict] = {}

    def _updateErrorTypes(self, foundErrorsTypes, testName):
        for foundErrorType in foundErrorsTypes:
            if foundErrorType not in self.errorTypes:
                self.errorTypes[foundErrorType] = [testName]
            elif testName not in self.errorTypes[foundErrorType]:
                self.errorTypes[foundErrorType].append(testName)

    @staticmethod
    def _indicesIn(listStruct, searchTerm):
        return [idx for idx, k in enumerate(listStruct) if searchTerm in k]

    def _getEndSectionIndex(self, fileContent, startSectionIndex, testName):
        endSectionText = self.END_FAIL_SECTION + testName

        endSectionIndex = self._indicesIn(fileContent[startSectionIndex:], endSectionText)
        if endSectionIndex:
            endSectionIndex = endSectionIndex[0]

        return endSectionIndex + startSectionIndex

    def _processErrorSection(self, fileContent, startSectionIndex, endSectionIndex):
        """
        Check for specific exceptions
        """
        errorContent = list(fileContent[startSectionIndex:endSectionIndex])
        expectedErrors = ["selenium.common.exceptions",
                          "CommonCode.CustomExceptions",
                          "AssertionError:",
                          "AttributeError:"
                          ]

        matchedEntries = []
        for line in errorContent:
            for expectedError in expectedErrors:
                if expectedError in line:
                    matchedEntries.append(line)

        return matchedEntries

    def _processFile(self, filePath):
        with open(filePath, "r", encoding="utf-8") as fp:
            fileContent = [line.rstrip("\n") for line in fp.readlines()]
            failedTestSectionIndices = self._indicesIn(fileContent, self.START_FAIL_SECTION)
            for startSectionIndex in failedTestSectionIndices:
                matchObj = re.search("test_C(.*)", fileContent[startSectionIndex])
                if not matchObj:
                    print("error, no test found")
                    continue

                testName = matchObj.group(0)
                endSectionIndex = self._getEndSectionIndex(fileContent, startSectionIndex, testName)
                foundErrorsTypes = self._processErrorSection(fileContent, startSectionIndex, endSectionIndex)

                self._updateErrorTypes(foundErrorsTypes, testName)

    def _writeOutputFile(self):
        outputFilePath = os.path.join(self.folderPath, self.OUTPUT_FILE_NAME)

        with open(outputFilePath, "w", encoding="utf-8") as output:
            for errorType in sorted(self.errorTypes):
                output.write(f"\n\n>>> Error type: {errorType}, fail count: {len(self.errorTypes[errorType])}\n")
                for testName in self.errorTypes[errorType]:
                    output.write(f"{testName}\n")

    def _writeOutputToConsole(self):
        for errorType in sorted(self.errorTypes):
            print(f"\n\n>>> Error type: {errorType}")
            for testName in self.errorTypes[errorType]:
                print(testName)

    def processTestErrorsIntoTestTypes(self):
        """
        Class public method.
        Takes path to log files. Open each log file in a sequence and processess its contents.
        Results are written to output file.
        :param test_logs_path:
        :return:
        """
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
                        dest="folderPath",
                        help=helpText,
                        required=True)
    return parser.parse_args()


if __name__ == "__main__":
    parse_args = configureArgParse()
    folderPath = parse_args.folderPath

    assert os.path.isdir(folderPath)

    test_log_processor = ProcessTestErrorsIntoTestTypes(folderPath)
    test_log_processor.processTestErrorsIntoTestTypes()
