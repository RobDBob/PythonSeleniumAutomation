class DictionaryCaseInsensitive(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._keys = {k.lower(): k for k in self.keys()}

    def __setitem__(self, key, value):
        self._keys[key.lower()] = key
        super().__setitem__(key, value)

    def __getitem__(self, key):
        return super().__getitem__(self._keys[key.lower()])

    def __delitem__(self, key):
        super().__delitem__(self._keys[key.lower()])

    def __contains__(self, key):
        return key.lower() in self._keys

    def get(self, key, defaultValue=None):
        if defaultValue:
            return super().get(key, defaultValue)
        return super().get(key)
