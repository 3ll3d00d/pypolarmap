import logging
import math
import time
import typing
from collections.abc import Sequence

import numpy as np
from qtpy.QtCore import QModelIndex, Qt, QVariant, QAbstractListModel
from scipy import signal

WINDOW_MAPPING = {
    'Hann': signal.windows.hann,
    'Hamming': signal.windows.hamming,
    'Blackman-Harris': signal.windows.blackmanharris,
    'Nuttall': signal.windows.nuttall,
    'Tukey': signal.windows.tukey,
    'Rectangle': signal.windows.boxcar
}

REAL_WORLD_DATA = 'REALWORLD'

# events that listeners have to handle
LOAD_MEASUREMENTS = 'LOAD'
CLEAR_MEASUREMENTS = 'CLEAR'

logger = logging.getLogger('measurement')


class MeasurementModel(Sequence):
    '''
    Models a related collection of measurements
    Propagates events to listeners when the model changes
    Allows assorted analysis to be performed against those measurements.
    '''

    def __init__(self, display_model, m=None, listeners=None):
        self.__measurements = m if m is not None else []
        self.__listeners = listeners if listeners is not None else []
        self.__smoothingType = None
        self.__displayModel = display_model
        self.__displayModel.measurementModel = self
        self.__complexData = {}
        self.table = None
        super().__init__()

    def __getitem__(self, i):
        return self.__measurements[i]

    def __len__(self):
        return len(self.__measurements)

    def registerListener(self, listener):
        '''
        Registers a listener for changes to measurements. Must provide onMeasurementUpdate methods that take no args and
        an idx as well as a clear method.
        :param listener: the listener.
        '''
        self.__listeners.append(listener)

    def __propagateEvent(self, eventType, **kwargs):
        '''
        propagates the specified event to all listeners.
        :param eventType: the event type.
        :param kwargs: the event args.
        '''
        for l in self.__listeners:
            start = time.time()
            l.onUpdate(eventType, **kwargs)
            end = time.time()
            logger.debug(f"Propagated event: {eventType} to {l} in {round((end - start) * 1000)}ms")

    def load(self, measurements):
        '''
        Loads measurements.
        :param measurements: the measurements.
        '''
        if self.table is not None:
            self.table.beginResetModel()
        if len(self.__measurements) > 0:
            self.clear(reset=False)
        self.__measurements = measurements
        if self.table is not None:
            self.table.endResetModel()
        if len(self.__measurements) > 0:
            self.__complexData[REAL_WORLD_DATA] = [self._createFRData(x) for x in self.__measurements]
            self.__propagateEvent(LOAD_MEASUREMENTS)
        else:
            self.__propagateEvent(CLEAR_MEASUREMENTS)

    def clear(self, reset=True):
        '''
        Clears the loaded measurements.
        '''
        if self.table is not None and reset:
            self.table.beginResetModel()
        self.__measurements = []
        if self.table is not None and reset:
            self.table.endResetModel()
        self.__propagateEvent(CLEAR_MEASUREMENTS)

    def normalisationChanged(self):
        '''
        flags that the normalisation selection has changed.
        :param normalised: true if normalised.
        :param angle: the angle to normalise to.
        '''
        self.__propagateEvent(LOAD_MEASUREMENTS)

    def _createFRData(self, measurement):
        return XYData(name=measurement.display_name,
                      hAngle=measurement.h,
                      x=measurement.freq,
                      y=measurement.spl)

    def getMagnitudeData(self, type=REAL_WORLD_DATA, ref=1):
        '''
        Gets the magnitude data of the specified type from the model.
        :param type: the type.
        :param ref: the reference against which to scale the result in dB.
        :return: the data (if any)
        '''
        data = [x for x in self.__complexData[type]] if type in self.__complexData else []
        if self.__displayModel.normalised and self.can_normalise(type):
            target = next(
                (x for x in data if math.isclose(float(x.hAngle), float(self.__displayModel.normalisationAngle))), None)
            if target:
                data = [x.normalise(target) for x in data]
            else:
                print(f"Unable to normalise {self.__displayModel.normalisationAngle}")
        return data

    def can_normalise(self, type):
        '''
        :param type: the data type.
        :return: True if that type can be normalised.
        '''
        return type == REAL_WORLD_DATA

    def getContourData(self, type=REAL_WORLD_DATA):
        '''
        Generates data for contour plots from the analysed data sets.
        :param type: the type of data to retrieve.
        :return: the data as a dict with xyz keys.
        '''
        # convert to a table of xyz coordinates where x = frequencies, y = angles, z = magnitude
        mag = self.getMagnitudeData(type)
        return {
            'x': np.array([d.x for d in mag]).flatten(),
            'y': np.array([d.hAngle for d in mag]).repeat(mag[0].x.size),
            'z': np.array([d.y for d in mag]).flatten()
        }

    def smooth(self, smoothingType):
        '''
        Sets the smoothing type for log spaced data.
        :param smoothingType:
        '''
        self.__smoothingType = smoothingType
        self.__propagateEvent(LOAD_MEASUREMENTS)


class XYData:
    '''
    Value object for showing data on a magnitude graph.
    '''

    def __init__(self, name, hAngle, x, y):
        self.name = name
        self.hAngle = hAngle
        self.x = x
        self.y = y

    def normalise(self, target):
        '''
        Normalises the y value against the target y.
        :param target: the target.
        :return: a normalised XYData.
        '''
        return XYData(self.name, self.hAngle, self.x, self.y - target.y)


class Measurement:
    '''
    A single measurement taken in the real world.
    '''
    reflectionFreeZoneLimit = 10 ** -4

    def __init__(self, name, h=0, v=0, freq=np.array([]), spl=np.array([])):
        self.__name = name
        self.__h = h
        self.__v = v
        self.__freq = freq
        self.__spl = spl

    def mirror(self):
        return Measurement(self.__name, h=-self.h, v=-self.v, freq=self.freq, spl=self.spl)

    @property
    def h(self):
        return self.__h

    @property
    def v(self):
        return self.__v

    @property
    def name(self):
        return self.__name

    @property
    def freq(self):
        return self.__freq

    @property
    def spl(self):
        return self.__spl

    @property
    def display_name(self):
        '''
        :return: the display name of this measurement.
        '''
        return f"H{self.h}V{self.v}"

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.display_name}"


class MeasurementListModel(QAbstractListModel):
    '''
    A Qt table model to feed the measurements view.
    '''

    def __init__(self, model, parent=None):
        super().__init__(parent=parent)
        self._measurementModel = model
        self._measurementModel.table = self

    def rowCount(self, parent: QModelIndex = ...):
        return len(self._measurementModel)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        else:
            return QVariant(self._measurementModel[index.row()]._name)
