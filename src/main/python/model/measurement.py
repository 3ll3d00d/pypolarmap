import logging
import math
import time
import typing
from collections.abc import Sequence

import numpy as np
from qtpy.QtCore import QModelIndex, Qt, QVariant, QAbstractListModel
from scipy import signal

from meascalcs import fft, linToLog, calSpatial, calPolar, smooth, calPower
from model.log import to_millis

WINDOW_MAPPING = {
    'Hann': signal.windows.hann,
    'Hamming': signal.windows.hamming,
    'Blackman-Harris': signal.windows.blackmanharris,
    'Nuttall': signal.windows.nuttall,
    'Tukey': signal.windows.tukey,
    'Rectangle': signal.windows.boxcar
}

REAL_WORLD_DATA = 'REALWORLD'
COMPUTED_MODAL_DATA = 'MODAL'

# events that listeners have to handle
LOAD_MEASUREMENTS = 'LOAD'
ANALYSED = 'ANALYSED'
CLEAR_MEASUREMENTS = 'CLEAR'

logger = logging.getLogger('measurement')


class MeasurementModel(Sequence):
    '''
    Models a related collection of measurements
    Propagates events to listeners when the model changes
    Allows assorted analysis to be performed against those measurements.

    The analysis supported was described in http://www.diyaudio.com/forums/software-tools/318151-klippel-near-field-scanner-shoestring-post5493342.html

    1) Read in (M for measurement) M.linear.pres(M.angles, freq.lin)
    2) convert using LintoLog to M.log.pres(M.angles, Freq.log)
    3) convert M.log.pres to Modal.model(numModes,freq.log) using Spatial
    4) Modal.model is now a model of the sound radiation, basically the velocity distribution on some fictitious sphere of radius Source.radius, which can be used to find the Pressure response at any angle and frequency (although it is best to use the frequencies freq.log for the reconstruction.)
    5) the pressure response at some desired field location (R is reconstructed) R.pres(freq.log, R.angle, FieldRadius) is obtained by calling the Function CalPolar once for each field point and frequency.
    CalPolar needs a vector (a row) of the complex array Modal.model at the desired frequency Freq.log(Current Frequency) and the desired R.angle, Freq.log(Current Frequency) and FieldRadius (your farnum) as double real numbers. It also needs the assumed source.radius (your velnum) which is not the driver radius, but the radius of a sphere which is the same volume as the enclosure.
    '''

    def __init__(self, modalParameters, displayModel, m=None, listeners=None):
        self.__measurements = m if m is not None else []
        self.__listeners = listeners if listeners is not None else []
        self.__modalResponse = None
        self.__smoothingType = None
        self.__modalParameters = modalParameters
        self.__displayModel = displayModel
        self.__displayModel.measurementModel = self
        self.__complexData = {}
        self.__powerResponse = {}
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
            logger.debug(f"Propagated event: {eventType} to {l} in {round((end-start)*1000)}ms")

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

    def getMaxSample(self):
        '''
        :return: the size of the longest measurement.
        '''
        return max([x.size() for x in self.__measurements])

    def getMaxSampleValue(self):
        '''
        :return: the largest sample value in the measurement set.
        '''
        return max([max(x.max(), abs(x.min())) for x in self.__measurements])

    def normalisationChanged(self):
        '''
        flags that the normalisation selection has changed.
        :param normalised: true if normalised.
        :param angle: the angle to normalise to.
        '''
        self.__propagateEvent(ANALYSED)

    def analyseMeasuredData(self, left, right):
        '''
        creates a window based on the left and right parameters & applies it to all measurements (which propagates the
        ANALYSED event).
        :param left: the left parameters.
        :param right: the right parameters.
        '''
        a = time.time()
        completeWindow = self.createWindow(left, right)
        for m in self.__measurements:
            m.analyse(left['position'].value(), right['position'].value(), win=completeWindow)
        self.__complexData[REAL_WORLD_DATA] = [self._createFRData(x) for x in self.__measurements]
        b = time.time()
        logger.debug(f"Analysed {len(self)} real world measurements in {to_millis(a, b)}ms")
        self._computePowerResponse(REAL_WORLD_DATA)
        c = time.time()
        logger.debug(f"Analysed power response in {to_millis(b, c)}ms")

        self.analyseModal()
        d = time.time()
        logger.debug(f"Analysed modal response in {to_millis(c, d)}ms")
        self.__propagateEvent(ANALYSED)

    def _computePowerResponse(self, dataType):
        '''
        Calculates the power response of the specified type of data.
        :param dataType: the type of data to analyse.
        '''
        power = []
        for idx, lf in enumerate(self.__complexData[dataType][0].x):
            polarAtFreq = [x.y[idx] for x in self.__complexData[dataType]]
            result = calPower(np.array(polarAtFreq), lf, self.__modalParameters.boxRadius)
            power.append(result)
        self.__powerResponse[dataType] = ComplexData(name='power',
                                                     hAngle=None,
                                                     x=np.copy(self.__complexData[dataType][0].x),
                                                     y=np.array(power))

    def _createFRData(self, measurement):
        logData, logFreqs = linToLog(measurement.fftData, measurement._fs / measurement.fftPoints)
        return ComplexData(name=measurement.getDisplayName(),
                           hAngle=measurement._h,
                           x=logFreqs,
                           y=logData,
                           scaleFactor=2 / measurement.fftPoints)

    def createWindow(self, left, right):
        '''
        Creates a window which is made up of two sections, one which contains just ones and the other which is the left
        or right side of a particular window. The size of each section is drive by the percent selector (so 25% means
        75% ones and 25% actual window).
        :param left: the left params (as delivered via ui widgets)
        :param right: the right params
        :return: an ndarray describing the window.
        '''
        peak = self[0].peakIndex()
        leftWin = self._createHalfWindow(left, peak, 0)
        rightWin = self._createHalfWindow(right, peak, 1)
        completeWindow = np.concatenate((leftWin[1], leftWin[0], rightWin[0], rightWin[1]))
        return completeWindow

    def _createHalfWindow(self, params, peakIdx, side):
        '''
        Creates a window which is made up of two sections, one which contains just ones and the other which is the left
        or right side of a particular window. The size of each section is drive by the percent selector (so 25% means
        75% ones and 25% actual window).
        :param params: the params (as delivered via ui widgets)
        :param peakIdx: the position of the peak in the measurement.
        :param side: 0 if left, 1 if right.
        :return: a 2 part tuple made up of the ones and the window.
        '''
        length = abs(peakIdx - params['position'].value())
        windowLength = int(round(length * (params['percent'].value() / 100)))
        ones = np.ones(length - windowLength)
        window = np.split(self._getScipyWindowFunction(params['type'])(windowLength * 2), 2)[side]
        return ones, window

    def _getScipyWindowFunction(self, type):
        if type.currentText() in WINDOW_MAPPING:
            return WINDOW_MAPPING[type.currentText()]
        else:
            return WINDOW_MAPPING['Tukey']

    def analyseModal(self):
        '''
        Analyses the real world data to create a new modal model.
        '''
        if REAL_WORLD_DATA in self.__complexData:
            # compute the modal parameters
            self.__modalResponse = calSpatial([x.y for x in self.__complexData[REAL_WORLD_DATA]],
                                              self.__complexData[REAL_WORLD_DATA][0].x,
                                              np.radians([x._h for x in self.__measurements]),
                                              self.__modalParameters.measurementDistance,
                                              self.__modalParameters.driverRadius,
                                              self.__modalParameters.modalCoeffs,
                                              self.__modalParameters.transFreq,
                                              self.__modalParameters.lfGain,
                                              self.__modalParameters.boxRadius,
                                              self.__modalParameters.f0,
                                              self.__modalParameters.q0)
            np.savetxt('modal.csv', np.transpose(np.abs(self.__modalResponse)), delimiter=',')
            np.savetxt('freqs.csv', self.__complexData[REAL_WORLD_DATA][0].x, delimiter=',')
            # compute the polar response using the modal parameters
            modal = []
            logFreqs = self.__complexData[REAL_WORLD_DATA][0].x
            for angle in range(0, 182, 2):
                name = 'modal ' + str(angle)
                x = logFreqs
                y = []
                for idx, lf in enumerate(self.__complexData[REAL_WORLD_DATA][0].x):
                    modalData = self.__modalResponse[:, idx]
                    result = calPolar(modalData, angle, lf, self.__modalParameters.boxRadius)
                    y.append(result)
                modal.append(ComplexData(name=name, hAngle=angle, x=x, y=np.array(y)))
            self.__complexData[COMPUTED_MODAL_DATA] = modal
            self._computePowerResponse(COMPUTED_MODAL_DATA)

    def getMagnitudeData(self, type=REAL_WORLD_DATA, ref=1):
        '''
        Gets the magnitude data of the specified type from the model.
        :param type: the type.
        :param ref: the reference against which to scale the result in dB.
        :return: the data (if any)
        '''
        data = [x.getMagnitude(ref, self.__smoothingType) for x in
                self.__complexData[type]] if type in self.__complexData else []
        if self.__displayModel.normalised:
            target = next(
                (x for x in data if math.isclose(float(x.hAngle), float(self.__displayModel.normalisationAngle))), None)
            if target:
                data = [x.normalise(target) for x in data]
            else:
                print(f"Unable to normalise {self.__displayModel.normalisationAngle}")
        return data

    def getPowerResponse(self, type=REAL_WORLD_DATA, ref=1):
        '''
        gets the power response.
        :param type: the type.
        :return: the power response.
        '''
        power = self.__powerResponse.get(type, None)
        if power is not None:
            return power.getMagnitude(ref, self.__smoothingType)
        return None

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
        if REAL_WORLD_DATA in self.__complexData:
            self.__propagateEvent(ANALYSED)


class ComplexData:
    '''
    Value object for storing computed data derived, directly or indirectly, from a measurement.
    '''

    def __init__(self, name, hAngle, x, y, scaleFactor=1):
        self.name = name
        self.hAngle = hAngle
        self.x = x
        self.y = y
        self.scaleFactor = scaleFactor

    def getMagnitude(self, ref, smoothingType):
        y = np.abs(self.y) * self.scaleFactor / ref
        if smoothingType is not None and smoothingType != 'None':
            y = smooth(y, self.x, smoothingType)
        return XYData(self.name, self.hAngle, self.x, 20 * np.log10(y))

    def getPhase(self):
        return XYData(self.name, self.hAngle, self.x, np.angle(self.y))


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

    def __init__(self, name, h=0, v=0, fs=48000):
        self._name = name
        self._h = h
        self._v = v
        self._fs = fs
        self.samples = np.array([])
        self.window = np.array([])
        self.gatedSamples = np.array([])
        self.fftOutput = np.array([])
        self.fftPoints = 0

    def size(self):
        '''
        :return: no of samples in the measurement.
        '''
        return self.samples.size

    def min(self):
        '''
        :return: the min value in the samples.
        '''
        return np.nanmin(self.samples)

    def max(self):
        '''
        :return: the max value in the samples.
        '''
        return np.nanmax(self.samples)

    def peakIndex(self):
        '''
        :return: the index of the peak value in the samples.
        '''
        return np.nanargmax(self.samples)

    def firstReflectionIndex(self):
        '''
        :return: a guess at the location of the first reflection using scipy find_peaks_cwt
        '''
        peak = self.peakIndex()
        endIndex = self.size()
        lengthMs = (endIndex - peak) / self._fs * 1000
        if lengthMs > 50.0:
            search_end = peak + (round(self._fs / 20))
            logger.debug(
                f"{self} has {round(lengthMs)}ms from peak to end, searching 50ms ({peak}:{search_end}) for 1st reflection")
            to_search = self.samples[peak:search_end]
        else:
            to_search = self.samples[peak:]
        return next((i + peak for i in signal.find_peaks_cwt(to_search, np.arange(10, 20)) if i > 40), self.size() - 1)

    def startIndex(self):
        '''
        :return: a guess at where to put the left window.
        '''
        peakIdx = self.peakIndex()
        for idx, x in np.ndenumerate(self.samples[peakIdx:0:-1]):
            if abs(x) < self.reflectionFreeZoneLimit:
                return peakIdx - idx
        return 0

    def getDisplayName(self):
        '''
        :return: the display name of this measurement.
        '''
        return 'H' + str(self._h) + 'V' + str(self._v)

    def analyse(self, left, right, win=None):
        '''
        Applies the left and right gate to the measurement and runs FFT and linToLog against the windowed data.
        :param left: the left gate position.
        :param right: the right gate position.
        :param win: the window if any
        '''
        gatedSamples = self.samples[left:right]
        if win is not None:
            gatedSamples *= win
        self.window = win
        self.gatedSamples = gatedSamples
        self.fftData, self.fftPoints = fft(self.gatedSamples)

    def __repr__(self):
        return '{}: {}'.format(self.__class__.__name__, self.getDisplayName())


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
            m = self._measurementModel[index.row()]
            display_name = f"{m._name} ({m.size()})"
            return QVariant(display_name)

    def completeRendering(self, view):
        for x in range(0, 4):
            view.resizeColumnToContents(x)
