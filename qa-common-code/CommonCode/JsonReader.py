import json
import os
import os.path


class JsonReader(object):
    def __init__(self, source_file):
        self.sourceFile = source_file
        self.section = None

        if os.path.isfile(source_file):
            f = open(source_file, 'r')
            self.jsonFile = json.load(f)
        else:
            raise Exception('Unable to find configuration file: {0}'.format(source_file))

    def load(self, section_to_read):
        """get first list from configuration, for current implementation--- to expand"""

        self.section = self.jsonFile[section_to_read]
        return self.section

    def get_setting(self, setting, index=0):
        """Assumes there will be more options comma delimited"""

        if setting in self.section:
            value = self.section[setting].split(',')
            if len(value) > index:
                value = value[index]

            return value
        else:
            raise Exception("get_setting > key not found")

    def section_has_key(self, key):
        return key in self.section

    def config_has_key(self, key):
        return key in self.jsonFile

    def keys(self):
        return list(self.jsonFile.keys())
