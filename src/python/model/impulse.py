import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

WINDOW_MAPPING = {
    'Hann': signal.windows.hann,
    'Hamming': signal.windows.hamming,
    'Blackman-Harris': signal.windows.blackmanharris,
    'Nuttall': signal.windows.nuttall,
    'Tukey': signal.windows.tukey,
    'Rectangle': signal.windows.boxcar
}


class ImpulseModel:
    '''
    Allows a set of measurements to be displayed on a chart as impulse responses.
    '''

    def __init__(self, chart, left, right, mag):
        self._chart = chart
        self._cmap = plt.cm.get_cmap('tab20')
        self._axes = self._chart.canvas.figure.add_subplot(111)
        self._axes.spines['bottom'].set_position('center')
        self._axes.spines['right'].set_color('none')
        self._axes.spines['top'].set_color('none')
        self._axes.xaxis.set_ticks_position('bottom')
        self._axes.grid()
        self._curves = {}
        self._yRange = 1
        self._leftWindow = left
        self._rightWindow = right
        self._measurements = []
        self._showWindowed = False
        self._activeX = None
        self._setMaxSample(0)
        self._leftLine = None
        self._rightLine = None
        self._magnitudeModel = mag

    def _setMaxSample(self, maxSample):
        self._maxSample = maxSample
        self._cacheUngatedXValues()
        self._activeX = self._ungatedXValues

    def _cacheUngatedXValues(self):
        self._ungatedXValues = np.arange(self._maxSample)

    def _cacheGatedXValues(self):
        '''
        Caches x values for the gated data which ranges from the left to the right window gate positions.
        :return:
        '''
        self._gatedXValues = np.arange(start=self._leftWindow['position'].value(),
                                       stop=self._rightWindow['position'].value())

    def accept(self, measurements):
        '''
        Accepts a fresh set of measurements.
        :param measurements: the measurements.
        :return:
        '''
        self._measurements = measurements
        if len(measurements) > 0:
            self._setMaxSample(max([x.size() for x in measurements]))
            self._yRange = max([max(x.max(), abs(x.min())) for x in measurements])
        else:
            self._setMaxSample(0)
            self._yRange = 1
        self._leftWindow['position'].setMaximum(self._maxSample-1)
        self._leftWindow['position'].setValue(measurements[0].startIndex())
        self._rightWindow['position'].setMaximum(self._maxSample)
        self._rightWindow['position'].setValue(measurements[0].firstReflectionIndex())
        self._axes.set_ylim(bottom=-self._yRange, top=self._yRange)
        self._axes.set_xlim(left=0, right=np.amax(self._activeX))

    def onMeasurementUpdate(self, idx):
        '''
        Allows the chart to react when a measurement active status is toggled.
        :param idx: the index of the toggled measurement.
        :return:
        '''
        self._displayActiveData(updatedIdx=idx)

    def display(self):
        '''
        Renders the plot by adding the legend, displaying all active measurements and initialising the left and right windows
        to the edges of the samples.
        :return:
        '''
        self._displayActiveData()
        self.updateLeftWindowPosition()
        self.updateRightWindowPosition()

    def _addPlotForMeasurement(self, idx, measurement):
        '''
        adds the measurement to the chart (using the measurement idx to control which pen is used to ensure consistent colour schemes)
        :param idx: the idx.
        :param measurement: the measurement itself.
        :return:
        '''
        cIdx = idx if idx == 0 or idx < len(self._cmap.colors) else len(self._cmap.colors) % idx
        colour = self._cmap.colors[cIdx]
        self._curves[measurement.getDisplayName()] = self._axes.plot(self._activeX, self._getY(measurement),
                                                                     linewidth=2, antialiased=True, linestyle='solid',
                                                                     color=colour)[0]

    def _getY(self, measurement):
        '''
        gets the y values for this measurement, uses the gated samples if _showWindowed else the raw samples.
        :param measurement: the measurement.
        :return: the y values.
        '''
        return measurement.gatedSamples if self._showWindowed else measurement.samples

    def updateLeftWindowPosition(self):
        '''
        pushes the left window spinner value to the line position, creating the line if necessary
        :return:
        '''
        value = self._leftWindow['position'].value()
        if self._leftLine:
            self._leftLine.set_xdata([value, value])
        else:
            self._leftLine = self._axes.axvline(x=value, linestyle='--')
        if value > self._rightWindow['position'].value():
            self._rightWindow['position'].setValue(value + 1)
            self.updateRightWindowPosition()
        self._chart.canvas.draw()

    def _propagateLeftWindow(self):
        '''
        pushes the left line position to the left window spinner
        :return:
        '''
        self._leftWindow['position'].setValue(round(self._leftLine.value()))
        self.updateLeftWindowPosition()

    def updateRightWindowPosition(self):
        '''
        pushes the right window spinner value to the line position, creating the line if necessary
        :return:
        '''
        value = self._rightWindow['position'].value()
        if self._rightLine:
            self._rightLine.set_xdata([value, value])
        else:
            self._rightLine = self._axes.axvline(x=value, linestyle='--')
        if value <= self._leftWindow['position'].value():
            self._leftWindow['position'].setValue(value - 1)
            self.updateLeftWindowPosition()
        self._chart.canvas.draw()

    def _propagateRightWindow(self):
        '''
        pushes the right line position to the right window spinner
        :return:
        '''
        self._rightWindow['position'].setValue(round(self._rightLine.value()))
        self.updateRightWindowPosition()

    def zoomToWindow(self):
        '''
        sets the x axis range to the positions of the left and right windows.
        :return:
        '''
        self._axes.set_xlim(left=self._leftWindow['position'].value() - 1,
                            right=self._rightWindow['position'].value() + 1)
        self._chart.canvas.draw()

    def toggleWindowed(self):
        '''
        toggles which charts are displayed.
        If we switch to windowed view then it creates a window based on the type
        and position specified, removes existing plots, adds the window as a plot to the chart, applies that window to
        the measurements and propagates the new windowed data to the magnitude model.
        If we switch to unwindowed then it simply reinstates the raw data.
        :return: the windowed data.
        '''
        self._showWindowed = not self._showWindowed
        if self._showWindowed:
            self._cacheGatedXValues()
            self._activeX = self._gatedXValues
            self._peakIndex = self._measurements[0].peakIndex()
            for x in self._measurements:
                self._applyWindow(self._leftWindow, self._rightWindow, self._peakIndex, x)
        else:
            self._activeX = self._ungatedXValues
            self.updateLeftWindowPosition()
            self.updateRightWindowPosition()
        self._displayActiveData()

    def _displayActiveData(self, updatedIdx=None):
        '''
        Ensures the currently active data is visible on the chart.
        :return:
        '''
        for idx, m in enumerate(self._measurements):
            if updatedIdx is None or updatedIdx == idx:
                curve = self._curves.get(m.getDisplayName())
                if m._active:
                    if curve:
                        curve.set_data(self._activeX, self._getY(m))
                    else:
                        self._addPlotForMeasurement(idx, m)
                else:
                    if curve:
                        curve.remove()
                        del self._curves[m.getDisplayName()]
        self._chart.canvas.draw()

    def _applyWindow(self, left, right, peak, measurement):
        '''
        creates a window based on the left and right parameters.
        :param left: the left parameters.
        :param right: the right parameters.
        :return:
        '''
        leftWin = self._createWindow0(left, peak, 0)
        rightWin = self._createWindow0(right, peak, 1)
        completeWindow = np.concatenate((leftWin[1], leftWin[0], rightWin[0], rightWin[1]))
        measurement.gated(left['position'].value(), right['position'].value(), win=completeWindow)

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
