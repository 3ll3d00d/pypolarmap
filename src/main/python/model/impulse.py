import logging
import time

import numpy as np

from model.log import to_millis
from model.measurement import CLEAR_MEASUREMENTS, LOAD_MEASUREMENTS, ANALYSED

RIGHT_WINDOW_PAD = 50

LEFT_WINDOW_PAD = 30

NAME = 'impulse'

logger = logging.getLogger(NAME)


class ImpulseModel:
    '''
    Allows a set of measurements to be displayed on a chart as impulse responses.
    '''

    def __init__(self, chart, left, right, measurementModel):
        self._chart = chart
        self.name = NAME
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
        self.__visible_measurement_indexes = []

    def __repr__(self):
        return self.__class__.__name__

    def selection_changed(self, selected, deselected):
        ''' notifies the impulse model when the selection changes '''
        drawn = False
        for i in deselected.indexes():
            self.__visible_measurement_indexes.remove(i.row())
            self.__change_visibility(i.row(), False)
            drawn = True
        for i in selected.indexes():
            self.__visible_measurement_indexes.append(i.row())
            self.__change_visibility(i.row(), True)
            drawn = True
        if drawn:
            self._chart.canvas.draw_idle()

    def __change_visibility(self, idx, visible):
        '''
        Change the visibility of the measurement at the specified index.
        :param idx: the index.
        :param visible: true if it should be visible.
        '''
        if idx < len(self._measurementModel):
            curve_name = self._measurementModel[idx].getDisplayName()
            if curve_name in self._curves:
                self._curves[curve_name].set_visible(visible)

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
            start = time.time()
            self._setMaxSample(self._measurementModel.getMaxSample())
            self._leftWindow['position'].blockSignals(True)
            self._leftWindow['position'].setMaximum(self._maxSample - 1)
            self._leftWindow['position'].setValue(max(0, self._measurementModel[0].startIndex()))
            self._leftWindow['position'].blockSignals(False)
            self._rightWindow['position'].blockSignals(True)
            self._rightWindow['position'].setMaximum(self._maxSample)
            self._rightWindow['position'].setValue(min(self._maxSample, self._measurementModel[0].peakIndex() + 600))
            self._rightWindow['position'].blockSignals(False)
            mid = time.time()
            logger.debug(f"updated window parameters {to_millis(start, mid)}ms")
            self.updateLeftWindow(draw=False)
            end = time.time()
            logger.debug(f"Updated chart controls in {to_millis(mid, end)}ms")
            self._displayData(updatedIdx=kwargs.get('idx', None))
        elif type == CLEAR_MEASUREMENTS:
            self._setMaxSample(0)
            self._leftWindow['position'].blockSignals(True)
            self._leftWindow['position'].setMaximum(0)
            self._leftWindow['position'].setValue(0)
            self._leftWindow['position'].blockSignals(False)
            self._rightWindow['position'].blockSignals(True)
            self._rightWindow['position'].setMaximum(1)
            self._rightWindow['position'].setValue(1)
            self._rightWindow['position'].blockSignals(False)
            self._showWindowed = False
            self._activeX = None
            self.clear()
        elif type == ANALYSED:
            pass

    def findFirstPeak(self):
        '''
        Searches for the 1st reflection and updates the right window to that location.
        '''
        if len(self._measurementModel) > 0:
            from app import wait_cursor
            with wait_cursor('Finding peak in first measurement'):
                start = time.time()
                self._rightWindow['position'].setValue(self._measurementModel[0].firstReflectionIndex())
                end = time.time()
                logger.debug(f"Found peaks in {to_millis(start, end)}ms")
                self.updateRightWindow()

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
                                                                     color=self._chart.getColour(idx, mCount),
                                                                     visible=False)[0]

    def _getY(self, m, ref):
        '''
        gets the y values for this measurement, uses the gated samples if _showWindowed else the raw samples.
        :param m: the measurement.
        :return: the y values (as a percentage of the max value)
        '''
        return (self._zeroPadGated(m.gatedSamples) if self._showWindowed else m.samples) / ref * 100

    def updateLeftWindow(self, draw=True):
        ''' pushes the left window spinner value to the line position, creating the line if necessary '''
        self._redrawWindow(draw)

    def updateRightWindow(self, draw=True):
        ''' pushes the right window spinner value to the line position, creating the line if necessary '''
        self._redrawWindow(draw)

    def is_window_valid(self):
        ''' :return True if left < right '''
        return self._leftWindow['position'].value() < self._rightWindow['position'].value()

    def _redrawWindow(self, draw=True):
        '''
        Draws the actual window on the screen.
        '''
        if self.is_window_valid():
            window = self._zeroPadGated(self._measurementModel.createWindow(self._leftWindow, self._rightWindow)) * 100
            if self._windowLine:
                self._windowLine.set_data(self._activeX, window)
            else:
                self._windowLine = self._axes.plot(self._activeX, window, 'g--')[0]
            x_min = max(0, self._leftWindow['position'].value() - LEFT_WINDOW_PAD)
            x_max = min(self._maxSample, self._rightWindow['position'].value() + RIGHT_WINDOW_PAD)
            self._axes.set_xlim(left=x_min, right=x_max)
            if draw:
                self._chart.canvas.draw_idle()

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

    def zoomIn(self, draw=True):
        '''
        sets the x axis range to the positions of the left and right windows (+/- a bit on each side).
        '''
        self._axes.set_xlim(left=max(0, self._leftWindow['position'].value() - 30),
                            right=min(self._rightWindow['position'].value() + 100, self._maxSample))
        if draw:
            self._chart.canvas.draw_idle()

    def zoomOut(self, draw=True):
        '''
        sets the x axis range to the x range
        :return:
        '''
        if self._activeX is not None:
            self._axes.set_xlim(left=0, right=np.nanmax(self._activeX))
            if draw:
                self._chart.canvas.draw_idle()

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
        start = time.time()
        self._showWindowed = True
        if len(self._measurementModel) > 0:
            self._redrawWindow(draw=False)
            self._measurementModel.analyseMeasuredData(self._leftWindow, self._rightWindow)
            self._displayData()
            end = time.time()
            logger.debug(f"in {to_millis(start, end)}ms")

    def _displayData(self, updatedIdx=None):
        '''
        Ensures the data is visible on the chart.
        '''
        start = time.time()
        ref = self._measurementModel.getMaxSampleValue()
        for idx, m in enumerate(self._measurementModel):
            if updatedIdx is None or updatedIdx == idx:
                curve = self._curves.get(m.getDisplayName())
                if curve:
                    curve.set_data(self._activeX, self._getY(m, ref))
                else:
                    self._addPlotForMeasurement(idx, m, len(self._measurementModel))
        mid = time.time()
        self._chart.canvas.draw_idle()
        end = time.time()
        logger.debug(f"Updated curves in {to_millis(start, mid)}ms, redrew canvas in {to_millis(mid, end)}ms")

    def clear(self):
        '''
        clears the graph.
        '''
        self._axes.clear()
        self._initChart()
        self._curves = {}
        self.__visible_measurement_indexes = []
        self._windowLine = None
