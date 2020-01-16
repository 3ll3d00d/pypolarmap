LOGGING_LEVEL = 'logging/level'
LOGGING_BUFFER_SIZE = 'logging/buffer_size'
DISPLAY_DB_RANGE = 'display/db_range'
DISPLAY_COLOUR_MAP = 'display/colour_map'
DISPLAY_POLAR_360 = 'display/polar_360'

DEFAULT_PREFS = {
    LOGGING_LEVEL: 'INFO',
    LOGGING_BUFFER_SIZE: 5000,
    DISPLAY_DB_RANGE: 60,
    DISPLAY_COLOUR_MAP: 'bgyw',
    DISPLAY_POLAR_360: False
}

TYPES = {
    DISPLAY_DB_RANGE: int,
    DISPLAY_POLAR_360: bool,
    LOGGING_BUFFER_SIZE: int
}


class Preferences:
    def __init__(self, settings):
        self.__settings = settings

    def has(self, key):
        '''
        checks for existence of a value.
        :param key: the key.
        :return: True if we have a value.
        '''
        return self.get(key) is not None

    def get(self, key, default_if_unset=True):
        '''
        Gets the value, if any.
        :param key: the settings key.
        :param default_if_unset: if true, return a default value.
        :return: the value.
        '''
        default_value = DEFAULT_PREFS.get(key, None) if default_if_unset is True else None
        value_type = TYPES.get(key, None)
        if value_type is not None:
            return self.__settings.value(key, defaultValue=default_value, type=value_type)
        else:
            return self.__settings.value(key, defaultValue=default_value)

    def get_all(self, prefix):
        '''
        Get all values with the given prefix.
        :param prefix: the prefix.
        :return: the values, if any.
        '''
        self.__settings.beginGroup(prefix)
        try:
            return set(filter(None.__ne__, [self.__settings.value(x) for x in self.__settings.childKeys()]))
        finally:
            self.__settings.endGroup()

    def set(self, key, value):
        '''
        sets a new value.
        :param key: the key.
        :param value:  the value.
        '''
        if value is None:
            self.__settings.remove(key)
        else:
            self.__settings.setValue(key, value)

    def clear_all(self, group):
        ''' clears all in the group '''
        self.__settings.beginGroup(group)
        try:
            for x in self.__settings.childKeys():
                self.__settings.remove(x)
        finally:
            self.__settings.endGroup()

    def clear(self, key):
        '''
        Removes the stored value.
        :param key: the key.
        '''
        self.set(key, None)
