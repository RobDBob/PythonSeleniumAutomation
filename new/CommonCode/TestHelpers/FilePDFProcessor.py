import os
import PyPDF2
from CommonCode.API.APIHelper import cleanUpRawResponseText


class PDFHelper:
    def __init__(self, locationFolder):
        self.locationFolder = locationFolder

    def getTextFromLastDownloadedPDF(self):
        downloadedFiles = os.listdir(self.locationFolder)
        sortedFiles = sorted(downloadedFiles, key=lambda x: os.path.getmtime(os.path.join(self.locationFolder, x)), reverse=True)
        lastDownloadedFile = sortedFiles[0] if sortedFiles else None
        if lastDownloadedFile:
            return self.getTextContentFromPDFFile(lastDownloadedFile)
        raise FileNotFoundError(f"File not found in path {self.locationFolder}")

    def getTextContentFromPDFFile(self, fileName):
        filePath = os.path.join(self.locationFolder, fileName)
        pageText = ""
        with open(filePath, 'rb') as file:
            pdfReader = PyPDF2.PdfReader(file)
            numberOfPages = len(pdfReader.pages)

            for pageNumber in range(numberOfPages):
                page = pdfReader.pages[pageNumber]
                pageText += page.extract_text()

            if pageText.strip():
                return pageText.encode("utf-8").decode("unicode_escape")
            raise FileNotFoundError(f"PDF file '{filePath}' does not contain any text.")

    def getTextSplitByNewLineChar(self, fileName, newLineChar="\n"):
        cleanText = []
        text = self.getTextContentFromPDFFile(fileName)
        for t in text.split(newLineChar):
            cleanText.append(cleanUpRawResponseText(t))
        return cleanText
