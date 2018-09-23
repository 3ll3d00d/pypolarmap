LOGGING_LEVEL = 'logging/level'
MODAL_BOX_RADIUS = 'modal/box_radius'
MODAL_LF_GAIN = 'modal/lf_gain'
MODAL_TRANS_FREQ = 'modal/trans_freq'
MODAL_Q0 = 'modal/q0'
MODAL_F0 = 'modal/f0'
MODAL_COEFFS = 'modal/coeffs'
MODAL_DRIVER_RADIUS = 'modal/driver_radius'
MODAL_MEASUREMENT_DISTANCE = 'modal/measurement_distance'
DISPLAY_DB_RANGE = 'display/db_range'
DISPLAY_COLOUR_MAP = 'display/colour_map'

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
    DISPLAY_DB_RANGE: 60,
    DISPLAY_COLOUR_MAP: 'bgyw'
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
    DISPLAY_DB_RANGE: int
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

    def clear(self, key):
        '''
        Removes the stored value.
        :param key: the key.
        '''
        self.set(key, None)
