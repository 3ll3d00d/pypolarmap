import typing
from collections.abc import Sequence

import numpy as np
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant, QEvent
from PyQt5.QtWidgets import QItemDelegate
from scipy import signal

from meascalcs import fft, linToLog, calSpatial, calPolar

WINDOW_MAPPING = {
    'Hann': signal.windows.hann,
    'Hamming': signal.windows.hamming,
    'Blackman-Harris': signal.windows.blackmanharris,
    'Nuttall': signal.windows.nuttall,
    'Tukey': signal.windows.tukey,
    'Rectangle': signal.windows.boxcar
}

FR_MAGNITUDE_DATA = 'FR'
MODAL_MAGNITUDE_DATA = 'MODAL'

# events that listeners have to handle
LOAD_MEASUREMENTS = 'LOAD'
TOGGLE_MEASUREMENT = 'TOGGLE'
ANALYSED = 'ANALYSED'
CLEAR_MEASUREMENTS = 'CLEAR'


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

    def __init__(self, m=None, listeners=None):
        self._measurements = m if m is not None else []
        self._listeners = listeners if listeners is not None else []
        self.__modalResponse = None
        self.__polarModel = None
        self.__magnitudeData = {}
        self.__modalMagnitudeData = {}
        super().__init__()

    def __getitem__(self, i):
        return self._measurements[i]

    def __len__(self):
        return len(self._measurements)

    def registerListener(self, listener):
        '''
        Registers a listener for changes to measurements. Must provide onMeasurementUpdate methods that take no args and
        an idx as well as a clear method.
        :param listener: the listener.
        '''
        self._listeners.append(listener)

    def _propagateEvent(self, type, **kwargs):
        '''
        propagates the specified event to all listeners.
        :param type: the event type.
        :param kwargs: the event args.
        '''
        for l in self._listeners:
            l.onUpdate(type, **kwargs)

    def toggleState(self, idx):
        '''
        Toggles state and tells any listeners.
        :param idx: the updated measurement index.
        '''
        self._measurements[idx].toggleState()
        self._propagateEvent(TOGGLE_MEASUREMENT, idx=idx)

    def load(self, measurements):
        '''
        Loads measurements.
        :param measurements: the measurements.
        '''
        self._measurements = measurements
        self._propagateEvent(LOAD_MEASUREMENTS)

    def clear(self):
        '''
        Clears the loaded measurements.
        '''
        self._measurements = []
        self._propagateEvent(CLEAR_MEASUREMENTS)

    def getMaxSample(self):
        '''
        :return: the size of the longest measurement.
        '''
        return max([x.size() for x in self._measurements])

    def getMaxSampleValue(self):
        '''
        :return: the largest sample value in the measurement set.
        '''
        return max([max(x.max(), abs(x.min())) for x in self._measurements])

    def generateMagnitudeResponse(self, left, right, peak):
        '''
        creates a window based on the left and right parameters & applies it to all measurements.
        :param left: the left parameters.
        :param right: the right parameters.
        :return:
        '''
        leftWin = self._createWindow0(left, peak, 0)
        rightWin = self._createWindow0(right, peak, 1)
        completeWindow = np.concatenate((leftWin[1], leftWin[0], rightWin[0], rightWin[1]))
        for m in self._measurements:
            m.analyse(left['position'].value(), right['position'].value(), win=completeWindow)
        self.__magnitudeData[FR_MAGNITUDE_DATA] = [self._createFRMagnitudeData(x) for x in self._measurements]
        self._propagateEvent(ANALYSED)

    def _createFRMagnitudeData(self, measurement):
        logData, logFreqs = linToLog(measurement.fftData, measurement._fs / measurement.fftPoints)
        return MagnitudeData(measurement.getDisplayName(), x=logFreqs, y=np.abs(logData) * 2 / measurement.fftPoints,
                             visibleFunc=measurement.isActive)

    def _createWindow0(self, params, peakIdx, side):
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

    def generateModalResponse(self, modalParameters):
        '''
        Calls calSpatial against this set of measurements and then calPolar to generate the computed polar model.
        '''
        if FR_MAGNITUDE_DATA in self.__magnitudeData:
            self.__modalResponse = calSpatial([x.y for x in self.__magnitudeData[FR_MAGNITUDE_DATA]],
                                              self.__magnitudeData[FR_MAGNITUDE_DATA][0].x,
                                              np.radians([x._h for x in self._measurements]),
                                              modalParameters.measurementDistance,
                                              modalParameters.driverRadius, modalParameters.modalCoeffs,
                                              modalParameters.transFreq, modalParameters.lfGain,
                                              modalParameters.boxRadius, modalParameters.f0, modalParameters.q0)
            self.generatePolarModel(modalParameters)

    def generatePolarModel(self, modalParameters):
        '''
        Generates the reconstructed polar model.
        :param modalParameters: the modal parameters.
        '''
        x = []
        y = []
        z = []
        for idx, lf in enumerate(self.__magnitudeData[FR_MAGNITUDE_DATA][0].x):
            for angle in range(0, 185, 5):
                modalData = self.__modalResponse[:, idx]
                result = calPolar(modalData, angle, lf, modalParameters.boxRadius)
                x.append(lf)
                y.append(angle)
                z.append(result)
        self.__modalMagnitudeData = {'x': np.array(x), 'y': np.array(y),
                                     'z': 20 * np.log10(np.abs(np.array(z)))}

    def getMagnitudeData(self, type=FR_MAGNITUDE_DATA, ref=1):
        '''
        Gets the magnitude data of the specified type from the model.
        :param type: the type.
        :param ref: the reference against which to scale the result in dB.
        :return: the data (if any)
        '''
        return [x.rescale(ref) for x in self.__magnitudeData[type]] if type in self.__magnitudeData else []

    def getContourData(self, type=FR_MAGNITUDE_DATA):
        '''
        Generates data for contour plots from the analysed data sets.
        :param type: the type of data to retrieve.
        :return: the data as a dict with xyz keys.
        '''
        if type == FR_MAGNITUDE_DATA:
            # convert to a table of xyz coordinates where x = frequencies, y = angles, z = magnitude
            mag = self.getMagnitudeData(type)
            return {
                'x': np.array([d.x for d in mag]).flatten(),
                'y': np.array([x._h for x in self]).repeat(mag[0].x.size),
                'z': np.array([d.y for d in mag]).flatten()
            }
        elif type == MODAL_MAGNITUDE_DATA:
            return self.__modalMagnitudeData
        else:
            return None


class MagnitudeData:
    '''
    Value object for showing data on a magnitude graph.
    '''

    def __init__(self, name, x, y, visibleFunc):
        self.name = name
        self.x = x
        self.y = y
        self.__visibleFunc = visibleFunc

    @property
    def visible(self):
        return self.__visibleFunc()

    def rescale(self, ref):
        return MagnitudeData(self.name, self.x, 20 * np.log10(self.y / ref), self.__visibleFunc)


class Measurement:
    '''
    Models a single measurement.
    '''
    reflectionFreeZoneLimit = 10 ** -4

    def __init__(self, name, h=0, v=0, fs=48000):
        self._name = name
        self._h = h
        self._v = v
        self._fs = fs
        self._active = True
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
        return np.amin(self.samples)

    def max(self):
        '''
        :return: the max value in the samples.
        '''
        return np.amax(self.samples)

    def peakIndex(self):
        '''
        :return: the index of the peak value in the samples.
        '''
        return np.argmax(self.samples)

    def firstReflectionIndex(self):
        '''
        :return: a guess at the location of the first reflection using scipy find_peaks_cwt
        '''
        peak = self.peakIndex()
        return next((i + peak for i in signal.find_peaks_cwt(self.samples[peak:], np.arange(10, 20)) if i > 40),
                    self.size() - 1)

    def startIndex(self):
        '''
        :return: a guess at where to put the left window.
        '''
        peakIdx = self.peakIndex()
        for idx, x in np.ndenumerate(self.samples[peakIdx:0:-1]):
            if abs(x) < self.reflectionFreeZoneLimit:
                return peakIdx - idx
        return 0

    def toggleState(self):
        '''
        sets whether this measurement is active or not.
        :return:
        '''
        self._active = not self._active

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

    def isActive(self):
        '''
        :return: if the measurement is currently active.
        '''
        return self._active

    def __repr__(self):
        return '{}: {}'.format(self.__class__.__name__, self.getDisplayName())


class MeasurementTableModel(QAbstractTableModel):
    '''
    A Qt table model to feed the measurements view.
    '''

    def __init__(self, model, parent=None):
        super().__init__(parent=parent)
        self._headers = ['File', 'Samples', 'H', 'V', 'Active']
        self._measurementModel = model

    def rowCount(self, parent: QModelIndex = ...):
        return len(self._measurementModel)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self._headers)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if (index.column() == 4):
            return super().flags(index) | Qt.ItemIsEditable
        else:
            return super().flags(index)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        else:
            if index.column() == 0:
                return QVariant(self._measurementModel[index.row()]._name)
            elif index.column() == 1:
                return QVariant(self._measurementModel[index.row()].size())
            elif index.column() == 2:
                return QVariant(self._measurementModel[index.row()]._h)
            elif index.column() == 3:
                return QVariant(self._measurementModel[index.row()]._v)
            elif index.column() == 4:
                return QVariant(self._measurementModel[index.row()]._active)
            else:
                return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self._headers[section])
        return QVariant()

    def accept(self, measurementModel):
        self.layoutAboutToBeChanged.emit()
        self._measurementModel = measurementModel
        self.layoutChanged.emit()

    def completeRendering(self, view):
        view.setItemDelegateForColumn(4, CheckBoxDelegate(None))
        for x in range(0, 5):
            view.resizeColumnToContents(x)

    def toggleState(self, idx):
        self._measurementModel.toggleState(idx)


# from https://stackoverflow.com/questions/17748546/pyqt-column-of-checkboxes-in-a-qtableview
class CheckBoxDelegate(QItemDelegate):
    """
    A delegate that places a fully functioning QCheckBox cell of the column to which it's applied & which propagates
    state changes to the owning measurement model.
    """

    def __init__(self, parent):
        QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        """
        Important, otherwise an editor is created if the user clicks in this cell.
        """
        return None

    def paint(self, painter, option, index):
        """
        Paint a checkbox without the label.
        """
        self.drawCheck(painter, option, option.rect, Qt.Unchecked if int(index.data()) == 0 else Qt.Checked)

    def editorEvent(self, event, model, option, index):
        '''
        Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton and this cell is editable. Otherwise do nothing.
        '''
        if not int(index.flags() & Qt.ItemIsEditable) > 0:
            return False

        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            # Change the checkbox-state
            model.toggleState(index.row())
            return True

        return False
