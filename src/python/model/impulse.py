import numpy as np
from scipy import signal

WINDOW_MAPPING={
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

    def __init__(self, chart, left, right):
        self._chart = chart
        self._chart.getPlotItem().enableAutoRange()
        self._leftWindow = left
        self._rightWindow = right
        self._measurements = []
        self._windowed = []
        self._activeData = self._measurements
        self._setMaxSample(0)
        self._leftLine = None
        self._rightLine = None

    def _setMaxSample(self, maxSample):
        self._maxSample = maxSample
        self._cacheXValues()

    def _cacheXValues(self):
        self._xValues = np.arange(self._maxSample)

    def accept(self, measurements):
        '''
        Accepts a fresh set of measurements.
        :param measurements: the measurements.
        :return:
        '''
        # TODO delete existing data?
        self._measurements = measurements
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
        updated = self._activeData[idx]
        curve = self._findCurve(updated.getDisplayName())
        if updated._active:
            if not curve:
                self._addPlotForMeasurement(idx, updated)
        else:
            if curve:
                self._chart.getPlotItem().removeItem(curve)
                self._chart.getPlotItem().legend.removeItem(updated.getDisplayName())

    def _findCurve(self, name):
        '''
        Finds the curve with the specified name.
        :param name: the name.
        :return: the curve.
        '''
        return next((x for x in self._chart.getPlotItem().listDataItems() if x.name() == name),
                    None)

    def display(self):
        '''
        Renders the plot by adding the legend, displaying all active measurements and initialising the left and right windows
        to the edges of the samples.
        :return:
        '''
        self._chart.getPlotItem().addLegend()
        for idx, measurement in enumerate(self._measurements):
            if measurement._active:
                self._addPlotForMeasurement(idx, measurement)
        self.updateLeftWindowPosition()
        self.updateRightWindowPosition()

    def _addPlotForMeasurement(self, idx, measurement):
        '''
        adds the measurement to the chart (using the measurement idx to control which pen is used to ensure consistent colour schemes)
        :param idx: the idx.
        :param measurement: the measurement itself.
        :return:
        '''
        self._chart.plot(self._xValues, measurement.samples, pen=(idx, len(self._measurements)),
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

    def showWindowed(self):
        '''
        creates a window based on the type and position specified, adds the window as a plot to the chart and applies
        that window to the measurements.
        :return:
        '''
        self._windowed = [self._applyWindow(self._leftWindow, self._rightWindow, x) for x in self._measurements]
        self._activeData = self._windowed
        self._setData()

    def showUnwindowed(self):
        '''
        Shows the unwindowed data.
        :return:
        '''
        self._activeData = self._measurements
        self._setData()

    def _setData(self):
        '''
        Updates the named plot items from the active measurement data.
        :return:
        '''
        for m in self._activeData:
            if m._active:
                curve = self._findCurve(m.getDisplayName())
                if curve:
                    curve.setData(m.samples)

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
        length = abs(peakIdx - params['position'].value())
        windowLength = int(round(length * (params['percent'].value() / 100)))
        ones = np.ones(length - windowLength)
        window = np.split(self._getScipyWindowFunction(params['type'])(windowLength * 2), 2)[side]
        return ones, window

    def _getScipyWindowFunction(self, type):
        if type.currentText() in WINDOW_MAPPING:
            return WINDOW_MAPPING[type.currentText()]
        else:
            return WINDOW_MAPPING['Hann']
