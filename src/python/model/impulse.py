import numpy as np
from scipy import signal

WINDOW_MAPPING = {
    'Hann': signal.windows.hann,
    'Hamming': signal.windows.hamming,
    'Blackman-Harris': signal.windows.blackmanharris,
    'Nuttall': signal.windows.nuttall,
    'Tukey': signal.windows.tukey
}


class ImpulseModel:
    '''
    Allows a set of measurements to be displayed on a chart as impulse responses.
    '''

    def __init__(self, chart, left, right, mag):
        self._chart = chart
        self._chart.getPlotItem().showGrid(x=True, y=True, alpha=0.75)
        self._chart.getPlotItem().enableAutoRange()
        self._leftWindow = left
        self._rightWindow = right
        self._measurements = []
        self._windowed = []
        self._showWindowed = False
        self._activeData = self._measurements
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
        self._activeData = measurements
        if len(measurements) > 0:
            self._setMaxSample(max([x.size() for x in measurements]))
        else:
            self._setMaxSample(0)
        self._leftWindow['position'].setMaximum(self._maxSample)
        self._leftWindow['position'].setValue(0)
        self._rightWindow['position'].setMaximum(self._maxSample)
        self._rightWindow['position'].setValue(self._maxSample)

    def onMeasurementUpdate(self, idx):
        '''
        Allows the chart to react when a measurement active status is toggled.
        :param idx: the index of the toggled measurement.
        :return:
        '''
        self._displayActiveData(updatedIdx=idx)

    def _findCurve(self, name):
        '''
        Finds the curve with the specified name.
        :param name: the name.
        :return: the curve.
        '''
        return next((x for x in self._chart.getPlotItem().listDataItems() if x.name() == name), None)

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
        self._chart.plot(self._activeX, measurement.samples, pen=(idx, len(self._activeData)),
                         name=measurement.getDisplayName())

    def updateLeftWindowPosition(self):
        '''
        pushes the left window spinner value to the line position, creating the line if necessary
        :return:
        '''
        value = self._leftWindow['position'].value()
        if self._leftLine:
            self._leftLine.setValue(value)
        else:
            self._leftLine = self._chart.addLine(x=value, movable=True, name='LeftWin')
            self._leftLine.sigPositionChangeFinished.connect(self._propagateLeftWindow)
        if value > self._rightWindow['position'].value():
            self._rightWindow['position'].setValue(value + 1)
            self.updateRightWindowPosition()

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
            self._rightLine.setValue(value)
        else:
            self._rightLine = self._chart.addLine(x=value, movable=True, name='RightWin')
            self._rightLine.sigPositionChangeFinished.connect(self._propagateRightWindow)
        if value <= self._leftWindow['position'].value():
            self._leftWindow['position'].setValue(value - 1)
            self.updateLeftWindowPosition()

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
        self._chart.getPlotItem().getViewBox().setXRange(self._leftWindow['position'].value() - 1,
                                                         self._rightWindow['position'].value() + 1, padding=0)

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
        self._clearChart()
        if self._showWindowed:
            self._leftLine.setVisible(False)
            self._rightLine.setVisible(False)
            self._cacheGatedXValues()
            self._activeX = self._gatedXValues
            self._windowed = [self._applyWindow(self._leftWindow, self._rightWindow, x) for x in self._measurements]
            self._activeData = self._windowed
            self._magnitudeModel.accept(self._windowed)
        else:
            self._leftLine.setVisible(True)
            self._rightLine.setVisible(True)
            self._activeX = self._ungatedXValues
            self._activeData = self._measurements
            self.updateLeftWindowPosition()
            self.updateRightWindowPosition()
        self._displayActiveData()

    def _clearChart(self):
        '''
        removes all items from the chart and legend.
        :return:
        '''
        for m in self._activeData:
            self._chart.getPlotItem().legend.removeItem(m.getDisplayName())
            curve = self._findCurve(m.getDisplayName)
            if curve:
                self._chart.getPlotItem().removeItem(curve)

    def _displayActiveData(self, updatedIdx=None):
        '''
        Ensures the currently active data is visible on the chart.
        :return:
        '''
        self._chart.getPlotItem().addLegend()
        for idx, m in enumerate(self._activeData):
            if updatedIdx is None or updatedIdx == idx:
                curve = self._findCurve(m.getDisplayName())
                if m._active:
                    if curve:
                        curve.setData(m.samples)
                    else:
                        self._addPlotForMeasurement(idx, m)
                else:
                    if curve:
                        self._chart.getPlotItem().removeItem(curve)
                        self._chart.getPlotItem().legend.removeItem(m.getDisplayName())

    def _applyWindow(self, left, right, measurement):
        '''
        creates a window based on the left and right parameters.
        :param left: the left parameters.
        :param right: the right parameters.
        :return:
        '''
        peak = measurement.peakIndex()
        leftWin = self._createWindow0(left, peak, 0)
        rightWin = self._createWindow0(right, peak, 1)
        completeWindow = np.concatenate((leftWin[1], leftWin[0], rightWin[0], rightWin[1]))
        gated = measurement.gated(left['position'].value(), right['position'].value())
        gated.samples = gated.samples * completeWindow
        return gated

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
