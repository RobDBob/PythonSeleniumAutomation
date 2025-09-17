import os
from argparse import Namespace
from enum import Enum
import yaml
from CommonCode.HelperFunctions import instanceDir


class ConfigClass:
    _settings: dict

    def __init__(self):
        self._settings = {}

    def __copy__(self):
        newInstance = type(self)()
        newInstance.__dict__.update(self.__dict__)
        return newInstance

    def update(self, incObject, replaceExisting=True):
        """
        Updated test context with values set in incoming obj
        This is used with either another TestContext or ParsedArgs
        :param incObject: incoming object
        :param replaceExisting: if TRUE new values replace existing, if FALSE: only new values are inserted
        :return:
        """

        if incObject is None:
            print("Nothing to set in TestContext.Update - returning")
            return
        if isinstance(incObject, Namespace):
            for attributeName in instanceDir(incObject):
                self._settings[attributeName] = getattr(incObject, attributeName) if replaceExisting else self._settings.get(attributeName, None)
        elif isinstance(incObject, dict):
            if replaceExisting:
                self._settings = {**self._settings, **incObject}
            else:
                self._settings = {**incObject, **self._settings}

    def setSetting(self, settingName, settingValue):
        """
        Sets RunSetting, updates existing
        """
        if isinstance(settingName, Enum):
            keyName = settingName.value
        else:
            keyName = settingName
        self._settings[keyName] = settingValue

    def getSetting(self, settingName, defaultValue=None):
        """
        Returns RunSetting from TestRun config
        """
        if isinstance(settingName, Enum):
            return self._settings.get(settingName.value, defaultValue)
        return self._settings.get(settingName, defaultValue)

    def setSettingFromYml(self, configFileName, configOption):
        """
        Config default folder is ConfigFiles
        """
        configPath = os.path.join("ConfigFiles", configFileName)

        if not os.path.exists(configPath):
            return

        with open(configPath, encoding="utf-8") as yamlfile:
            configInst = ConfigClass()
            configInst.update(yaml.full_load(yamlfile))
            self.setSetting(configOption, configInst)

    def getPrintable(self):
        def getPrintableFromObj(objDetailsToPrint):
            """
            Gets printable from a mix of self (testContext) and dictionaries
            """
            toPrint = {}
            for attributeName in instanceDir(objDetailsToPrint):
                attributeValue = getattr(objDetailsToPrint, attributeName)
                toPrint[attributeName] = {}

                if isinstance(attributeValue, ConfigClass):
                    toPrint[keyName] = ConfigClass.getPrintable(keyValue)

                elif isinstance(attributeValue, dict):
                    for keyName, keyValue in attributeValue.items():
                        if isinstance(keyValue, ConfigClass):
                            toPrint[attributeName][keyName] = ConfigClass.getPrintable(keyValue)
                        else:
                            toPrint[attributeName][keyName] = keyValue
                else:
                    toPrint[attributeName] = attributeValue
            return toPrint
        return getPrintableFromObj(self)
