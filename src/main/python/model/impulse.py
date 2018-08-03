import numpy as np

from model.measurement import CLEAR_MEASUREMENTS, LOAD_MEASUREMENTS, ANALYSED


class ImpulseModel:
    '''
    Allows a set of measurements to be displayed on a chart as impulse responses.
    '''

    def __init__(self, chart, left, right, measurementModel):
        self._chart = chart
        self.name = 'impulse'
        self._axes = self._chart.canvas.figure.add_subplot(111)
        self._initChart()
        self._curves = {}
        self._leftWindow = left
        self._rightWindow = right
        self._measurementModel = measurementModel
        self._measurementModel.registerListener(self)
        self._showWindowed = False
        self._activeX = None
        self._setMaxSample(0)
        self._windowLine = None

    def _initChart(self):
        self._axes.spines['bottom'].set_position('center')
        self._axes.spines['right'].set_color('none')
        self._axes.spines['top'].set_color('none')
        self._axes.xaxis.set_ticks_position('bottom')
        self._axes.set_ylim(bottom=-100, top=100)
        self._axes.grid()

    def _setMaxSample(self, maxSample):
        self._maxSample = maxSample
        self._activeX = np.arange(self._maxSample)

    def onUpdate(self, type, **kwargs):
        '''
        Allows the chart to react when the measurement model changes, handles active status toggle events only.
        :param idx: the index of the toggled measurement.
        :return:
        '''
        if type == LOAD_MEASUREMENTS:
            self._setMaxSample(self._measurementModel.getMaxSample())
            self._leftWindow['position'].setMaximum(self._maxSample - 1)
            self._leftWindow['position'].setValue(self._measurementModel[0].startIndex())
            self._rightWindow['position'].setMaximum(self._maxSample)
            self._rightWindow['position'].setValue(self._measurementModel[0].firstReflectionIndex())
            self.zoomOut()
            self.updateLeftWindow()
            self.updateRightWindow()
            self._displayData(updatedIdx=kwargs.get('idx', None))
        elif type == CLEAR_MEASUREMENTS:
            self._setMaxSample(0)
            self._leftWindow['position'].setMaximum(0)
            self._leftWindow['position'].setValue(0)
            self._rightWindow['position'].setMaximum(1)
            self._rightWindow['position'].setValue(1)
            self._showWindowed = False
            self._activeX = None
            self._windowLine = None
            self.clear()
        elif type == ANALYSED:
            pass

    def _addPlotForMeasurement(self, idx, measurement, mCount):
        '''
        adds the measurement to the chart (using the measurement idx to control which pen is used to ensure consistent colour schemes)
        :param idx: the idx.
        :param measurement: the measurement itself.
        :return:
        '''
        ref = self._measurementModel.getMaxSampleValue()
        self._curves[measurement.getDisplayName()] = self._axes.plot(self._activeX, self._getY(measurement, ref),
                                                                     linewidth=2, antialiased=True, linestyle='solid',
                                                                     color=self._chart.getColour(idx, mCount))[0]

    def _getY(self, m, ref):
        '''
        gets the y values for this measurement, uses the gated samples if _showWindowed else the raw samples.
        :param m: the measurement.
        :return: the y values (as a percentage of the max value)
        '''
        return (self._zeroPadGated(m.gatedSamples) if self._showWindowed else m.samples) / ref * 100

    def updateLeftWindow(self):
        '''
        pushes the left window spinner value to the line position, creating the line if necessary
        '''
        value = self._leftWindow['position'].value()
        if value > self._rightWindow['position'].value():
            self._rightWindow['position'].setValue(value + 1)
        self._redrawWindow()

    def updateRightWindow(self):
        '''
        pushes the right window spinner value to the line position, creating the line if necessary
        '''
        value = self._rightWindow['position'].value()
        if value <= self._leftWindow['position'].value():
            self._leftWindow['position'].setValue(value - 1)
        self._redrawWindow()

    def _redrawWindow(self, draw=True):
        '''
        Draws the actual window on the screen.
        '''
        window = self._zeroPadGated(self._measurementModel.createWindow(self._leftWindow, self._rightWindow)) * 100
        if self._windowLine:
            self._windowLine.set_data(self._activeX, window)
        else:
            self._windowLine = self._axes.plot(self._activeX, window, 'b--')[0]
        if draw:
            self._chart.canvas.draw()

    def _zeroPadGated(self, data):
        '''
        Zero pads the data using the left and right window as the marker points for padding if the data is gated.
        :param data: the data.
        :return: the zero padded data.
        '''
        if len(data) < self._maxSample:
            return np.concatenate((np.zeros(self._leftWindow['position'].value()), data,
                                   np.zeros(len(self._activeX) - self._rightWindow['position'].value())))
        else:
            return data

    def zoomIn(self):
        '''
        sets the x axis range to the positions of the left and right windows.
        :return:
        '''
        self._axes.set_xlim(left=max(0, self._leftWindow['position'].value() - 10),
                            right=min(self._rightWindow['position'].value() + 10, self._maxSample))
        self._chart.canvas.draw()

    def zoomOut(self):
        '''
        sets the x axis range to the x range
        :return:
        '''
        if self._activeX is not None:
            self._axes.set_xlim(left=0, right=np.nanmax(self._activeX))
            self._chart.canvas.draw()

    def removeWindow(self):
        '''
        simply reinstates the raw data.
        :return: the windowed data.
        '''
        self._showWindowed = False
        self._redrawWindow(draw=False)
        self._displayData()

    def applyWindow(self):
        '''
        applies the window to the data & makes this the viewable data.
        '''
        self._showWindowed = True
        if len(self._measurementModel) > 0:
            self._redrawWindow(draw=False)
            self._measurementModel.analyseMeasuredData(self._leftWindow, self._rightWindow)
            self._displayData()
            self.zoomIn()

    def _displayData(self, updatedIdx=None):
        '''
        Ensures the data is visible on the chart.
        '''
        ref = self._measurementModel.getMaxSampleValue()
        for idx, m in enumerate(self._measurementModel):
            if updatedIdx is None or updatedIdx == idx:
                curve = self._curves.get(m.getDisplayName())
                if curve:
                    curve.set_data(self._activeX, self._getY(m, ref))
                else:
                    self._addPlotForMeasurement(idx, m, len(self._measurementModel))
        self._chart.canvas.draw()

    def clear(self):
        '''
        clears the graph.
        '''
        self._axes.clear()
        self._initChart()
        self._curves = {}