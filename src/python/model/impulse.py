import numpy as np

from model.measurement import CLEAR_MEASUREMENTS, LOAD_MEASUREMENTS, ANALYSED


class ImpulseModel:
    '''
    Allows a set of measurements to be displayed on a chart as impulse responses.
    '''

    def __init__(self, chart, left, right, measurementModel):
        self._chart = chart
        self._axes = self._chart.canvas.figure.add_subplot(111)
        self._initChart()
        self._curves = {}
        self._yRange = 1
        self._leftWindow = left
        self._rightWindow = right
        self._measurementModel = measurementModel
        self._measurementModel.registerListener(self)
        self._showWindowed = False
        self._activeX = None
        self._setMaxSample(0)
        self._leftLine = None
        self._rightLine = None

    def _initChart(self):
        self._axes.spines['bottom'].set_position('center')
        self._axes.spines['right'].set_color('none')
        self._axes.spines['top'].set_color('none')
        self._axes.xaxis.set_ticks_position('bottom')
        self._axes.grid()

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

    def onUpdate(self, type, **kwargs):
        '''
        Allows the chart to react when the measurement model changes, handles active status toggle events only.
        :param idx: the index of the toggled measurement.
        :return:
        '''
        updateChart = True
        if type == LOAD_MEASUREMENTS:
            self._setMaxSample(self._measurementModel.getMaxSample())
            self._yRange = self._measurementModel.getMaxSampleValue()
            self._leftWindow['position'].setMaximum(self._maxSample - 1)
            self._leftWindow['position'].setValue(self._measurementModel[0].startIndex())
            self._rightWindow['position'].setMaximum(self._maxSample)
            self._rightWindow['position'].setValue(self._measurementModel[0].firstReflectionIndex())
        elif type == CLEAR_MEASUREMENTS:
            self._setMaxSample(0)
            self._yRange = 1
            self._leftWindow['position'].setMaximum(0)
            self._leftWindow['position'].setValue(0)
            self._rightWindow['position'].setMaximum(1)
            self._rightWindow['position'].setValue(1)
            self.clear()
        elif type == ANALYSED:
            updateChart = False
        if updateChart:
            self.zoomOut()
            self._axes.set_ylim(bottom=-self._yRange, top=self._yRange)
            self.updateLeftWindowPosition()
            self.updateRightWindowPosition()
            self._displayData(updatedIdx=kwargs.get('idx', None))

    def _addPlotForMeasurement(self, idx, measurement, mCount):
        '''
        adds the measurement to the chart (using the measurement idx to control which pen is used to ensure consistent colour schemes)
        :param idx: the idx.
        :param measurement: the measurement itself.
        :return:
        '''
        self._curves[measurement.getDisplayName()] = self._axes.plot(self._activeX, self._getY(measurement),
                                                                     linewidth=2, antialiased=True, linestyle='solid',
                                                                     color=self._chart.getColour(idx, mCount))[0]

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

    def zoomIn(self):
        '''
        sets the x axis range to the positions of the left and right windows.
        :return:
        '''
        self._axes.set_xlim(left=self._leftWindow['position'].value() - 1,
                            right=self._rightWindow['position'].value() + 1)
        self._chart.canvas.draw()

    def zoomOut(self):
        '''
        sets the x axis range to the x range
        :return:
        '''
        self._axes.set_xlim(left=0, right=np.nanmax(self._activeX))
        self._chart.canvas.draw()

    def removeWindow(self):
        '''
        simply reinstates the raw data.
        :return: the windowed data.
        '''
        self._showWindowed = False
        self._activeX = self._ungatedXValues
        self.updateLeftWindowPosition()
        self.updateRightWindowPosition()
        self._displayData()

    def applyWindow(self):
        '''
        applies the window to the data & makes this the viewable data.
        '''
        self._showWindowed = True
        if len(self._measurementModel) > 0:
            self._cacheGatedXValues()
            self._activeX = self._gatedXValues
            self._peakIndex = self._measurementModel[0].peakIndex()
            self._measurementModel.analyseMeasuredData(self._leftWindow, self._rightWindow, self._peakIndex)
            self._displayData()
            self.zoomIn()

    def _displayData(self, updatedIdx=None):
        '''
        Ensures the data is visible on the chart.
        '''
        for idx, m in enumerate(self._measurementModel):
            if updatedIdx is None or updatedIdx == idx:
                curve = self._curves.get(m.getDisplayName())
                if curve:
                    curve.set_data(self._activeX, self._getY(m))
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
