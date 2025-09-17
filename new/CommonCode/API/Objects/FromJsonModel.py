class FromJsonModel:
    def __init__(self, sourceJson: dict):
        self.sourceJson: dict = sourceJson

    def _getValue(self, keyName, defaultValue=""):
        return self.sourceJson.get(keyName, defaultValue)
