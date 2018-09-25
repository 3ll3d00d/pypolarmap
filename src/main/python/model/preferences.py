LOGGING_LEVEL = 'logging/level'
LOGGING_BUFFER_SIZE = 'logging/buffer_size'
MODAL_GROUP = 'modal'
MODAL_BOX_RADIUS = f"{MODAL_GROUP}/box_radius"
MODAL_LF_GAIN = f"{MODAL_GROUP}/lf_gain"
MODAL_TRANS_FREQ = f"{MODAL_GROUP}/trans_freq"
MODAL_Q0 = f"{MODAL_GROUP}/q0"
MODAL_F0 = f"{MODAL_GROUP}/f0"
MODAL_COEFFS = f"{MODAL_GROUP}/coeffs"
MODAL_DRIVER_RADIUS = f"{MODAL_GROUP}/driver_radius"
MODAL_MEASUREMENT_DISTANCE = f"{MODAL_GROUP}/measurement_distance"
DISPLAY_DB_RANGE = 'display/db_range'
DISPLAY_COLOUR_MAP = 'display/colour_map'
DISPLAY_SHOW_POWER_RESPONSE = 'display/show_power'
DISPLAY_POLAR_360 = 'display/polar_360'

DEFAULT_PREFS = {
    MODAL_BOX_RADIUS: 1.0,
    MODAL_LF_GAIN: 0.0,
    MODAL_TRANS_FREQ: 200,
    MODAL_Q0: 0.700,
    MODAL_F0: 70,
    MODAL_COEFFS: 14,
    MODAL_DRIVER_RADIUS: 0.15,
    MODAL_MEASUREMENT_DISTANCE: 1.00,
    LOGGING_LEVEL: 'INFO',
    LOGGING_BUFFER_SIZE: 5000,
    DISPLAY_DB_RANGE: 60,
    DISPLAY_COLOUR_MAP: 'bgyw',
    DISPLAY_SHOW_POWER_RESPONSE: True,
    DISPLAY_POLAR_360: False
}

TYPES = {
    MODAL_BOX_RADIUS: float,
    MODAL_LF_GAIN: float,
    MODAL_TRANS_FREQ: int,
    MODAL_Q0: float,
    MODAL_F0: int,
    MODAL_COEFFS: int,
    MODAL_DRIVER_RADIUS: float,
    MODAL_MEASUREMENT_DISTANCE: float,
    DISPLAY_DB_RANGE: int,
    DISPLAY_SHOW_POWER_RESPONSE: bool,
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
