import json
import os
import os.path


class JsonReader:
    section = None
    jsonFile: dict = None

    def __init__(self, sourceFile):
        self.sourceFile = sourceFile

        if os.path.isfile(sourceFile):
            with open(sourceFile, 'r', encoding="utf-8") as f:
                self.jsonFile = json.load(f)
        else:
            raise FileNotFoundError(f"Unable to find configuration file: {sourceFile}")

    def load(self, sectionToRead):
        """get first list from configuration, for current implementation--- to expand"""

        self.section = self.jsonFile.get(sectionToRead)
        return self.section

    def keys(self):
        return list(self.jsonFile.keys())
