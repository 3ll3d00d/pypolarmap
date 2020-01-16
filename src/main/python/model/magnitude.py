import logging

import numpy as np
from qtpy import QtCore
from matplotlib import animation
from qtpy.QtWidgets import QListWidgetItem

from model import configureFreqAxisFormatting, formatAxes_dBFS_Hz, setYLimits, SINGLE_SUBPLOT_SPEC, \
    calculate_dBFS_Scales
from model.measurement import REAL_WORLD_DATA, CLEAR_MEASUREMENTS, LOAD_MEASUREMENTS

logger = logging.getLogger('magnitude')


class MagnitudeModel:
    '''
    Allows a set of measurements to be displayed on a chart as magnitude responses.
    '''

    def __init__(self, chart, measurementModel, display_model, preferences, type=REAL_WORLD_DATA, modelListener=None,
                 subplotSpec=SINGLE_SUBPLOT_SPEC, showLegend=True, selector=None, depends_on=lambda: False):
        self._chart = chart
        self._axes = self._chart.canvas.figure.add_subplot(subplotSpec)
        formatAxes_dBFS_Hz(self._axes)
        self._curves = {}
        self._refreshData = False
        self._type = type
        self.name = f"magnitude_{self._type}"
        self._measurementModel = measurementModel
        self._modelListener = modelListener
        self._showLegend = showLegend
        self._measurementModel.registerListener(self)
        self.__display_model = display_model
        self._selector = selector
        self.__depends_on = depends_on
        if self._selector is not None:
            self._selector.itemSelectionChanged.connect(self.set_visible)
        self.updateDecibelRange(draw=False)

    def set_visible(self):
        ''' ensures the visible curves tracks the contents of the selector '''
        selected = [x.text() for x in self._selector.selectedItems()]
        for name, curve in self._curves.items():
            curve.set_visible(name in selected)
        self._chart.canvas.draw_idle()

    def __repr__(self):
        return self.name

    def shouldRefresh(self):
        return self._refreshData or self.__depends_on()

    def updateDecibelRange(self, draw=True):
        '''
        Updates the decibel range on the chart.
        '''
        if draw:
            setYLimits(self._axes, self.__display_model.dBRange)
            self._chart.canvas.draw_idle()

    def display(self):
        '''
        Updates the contents of the magnitude chart
        '''
        # TODO might need to update the ylim even if we haven't refreshed
        if self.shouldRefresh():
            # pressure
            data = self._measurementModel.getMagnitudeData(type=self._type, ref=1)
            current_names = [x.name for x in data]
            all_y = [x.y for x in data]
            for idx, x in enumerate(data):
                self._create_or_update_curve(x, self._axes, self._chart.getColour(idx, len(self._measurementModel)))
            # scales
            self._update_y_lim(np.concatenate(all_y), self._axes)
            # delete redundant data
            to_delete = [k for k in self._curves.keys() if k not in current_names]
            for d in to_delete:
                self._curves[d].remove()
                del self._curves[d]
                for item in self._selector.findItems(d, QtCore.Qt.MatchExactly):
                    self._selector.takeItem(self._selector.row(item))
            # legend
            if self._showLegend:
                lines = self._curves.values()
                if self._axes.get_legend() is not None:
                    self._axes.get_legend().remove()
                self._axes.legend(lines, [l.get_label() for l in lines], loc=8, ncol=4, fancybox=True, shadow=True)
            # selector
            if self._selector is not None:
                self._selector.selectAll()
            else:
                self._chart.canvas.draw_idle()
            self._refreshData = False
        else:
            ylim = self._axes.get_ylim()
            if ylim[1] - ylim[0] != self.__display_model.dBRange:
                self.updateDecibelRange()

    def _update_y_lim(self, data, axes):
        configureFreqAxisFormatting(axes)
        ymax, ymin, _, _ = calculate_dBFS_Scales(data, maxRange=self.__display_model.dBRange)
        axes.set_ylim(bottom=ymin, top=ymax)

    def _create_or_update_curve(self, data, axes, colour):
        curve = self._curves.get(data.name, None)
        if curve:
            curve.set_data(data.x, data.y)
        else:
            self._curves[data.name] = axes.semilogx(data.x, data.y,
                                                    linewidth=2,
                                                    antialiased=True,
                                                    linestyle='solid',
                                                    color=colour,
                                                    label=data.name)[0]
            if self._selector is not None:
                self._selector.addItem(QListWidgetItem(data.name, self._selector))

    def onUpdate(self, type, **kwargs):
        '''
        handles measurement model changes
        If event type is activation toggle then changes the associated curve visibility.
        If event type is analysis change then the model is marked for refresh.
        :param idx: the measurement idx.
        '''
        if self._modelListener:
            self._modelListener.onUpdate(type, kwargs)
        if type == LOAD_MEASUREMENTS:
            self._refreshData = True
        elif type == CLEAR_MEASUREMENTS:
            self.clear()

    def clear(self):
        '''
        clears the graph.
        '''
        self._axes.clear()
        self._curves = {}
        formatAxes_dBFS_Hz(self._axes)
        if self._selector is not None:
            self._selector.clear()


class AnimatedSingleLineMagnitudeModel:
    '''
    Allows a single measurement from a selection of magnitude data to be displayed on a chart.
    '''

    def __init__(self, chart, measurementModel, display_model, preferences, marker_data, type=REAL_WORLD_DATA,
                 subplotSpec=SINGLE_SUBPLOT_SPEC, redrawOnDisplay=True):
        self._chart = chart
        self._measurementModel = measurementModel
        self._measurementModel.registerListener(self)
        self._axes = self._chart.canvas.figure.add_subplot(subplotSpec)
        self._secondary_axes = self._axes.twinx()
        self._secondary_axes.set_ylim(bottom=0, top=30)
        formatAxes_dBFS_Hz(self._axes)
        self._type = type
        self.name = f"single-magnitude_{type}"
        self._refreshData = False
        self._type = type
        self.xPosition = None
        self.yPosition = None
        self._pressure_data = None
        self._pressure_curve = None
        self._pressure_marker = None
        self._di_curve = None
        self._di_marker = None
        self._vline = None
        self._ani = None
        self._y_range_update_required = False
        self._redrawOnDisplay = redrawOnDisplay
        self.__display_model = display_model
        self.__marker_data = marker_data

    def __repr__(self):
        return self.name

    def shouldRefresh(self):
        return self._refreshData

    def updateDecibelRange(self, draw=True):
        '''
        Updates the decibel range on the chart.
        '''
        self._y_range_update_required = True
        setYLimits(self._axes, self.__display_model.dBRange)
        if self._ani:
            # have to clear the blit cache to get the r grid to redraw as per
            # https://stackoverflow.com/questions/25021311/matplotlib-animation-updating-radial-view-limit-for-polar-plot
            self._ani._blit_cache.clear()
        if draw:
            self._chart.canvas.draw_idle()
            self._y_range_update_required = False

    def display(self):
        '''
        Gets fresh data and redraws.
        :return: true if it redrew.
        '''
        redrew = False
        if self.shouldRefresh():
            if self._pressure_curve is None:
                # pressure
                self._pressure_data = self._measurementModel.getMagnitudeData(type=self._type, ref=1)
                self._pressure_curve = self._axes.semilogx(self._pressure_data[0].x,
                                                           [np.nan] * len(self._pressure_data[0].x),
                                                           linewidth=2,
                                                           antialiased=True,
                                                           linestyle='solid')[0]
                self._pressure_marker = self._axes.plot(0, 0, 'bo', markersize=8)[0]
                all_data = [x.y for x in self._pressure_data]
                # line
                self._vline = self._axes.axvline(x=0, linewidth=2, color='gray', linestyle=':')
                # scales
                ymax, ymin, _, _ = calculate_dBFS_Scales(np.concatenate(all_data),
                                                         maxRange=self.__display_model.dBRange)
                self._axes.set_ylim(bottom=ymin, top=ymax, auto=False)
                configureFreqAxisFormatting(self._axes)
                self._y_range_update_required = False
                self._refreshData = False
                redrew = True
        else:
            if self._pressure_curve is not None:
                if self._y_range_update_required:
                    self.updateDecibelRange(self._redrawOnDisplay)
        # make sure we are animating
        if self._ani is None and self._pressure_data is not None:
            logger.info(f"Starting animation in {self.name}")
            self._ani = animation.FuncAnimation(self._chart.canvas.figure, self.redraw, interval=50,
                                                init_func=self.initAnimation, blit=True, save_count=50, repeat=False)
        return redrew

    def initAnimation(self):
        '''
        Inits a blank screen.
        :return: the curve artist.
        '''
        self._pressure_curve.set_ydata([np.nan] * len(self._pressure_data[0].x))
        return self._pressure_curve, self._pressure_marker, self._vline

    def __find_nearest_xy(self, curve):
        return np.argmax(curve.x >= self.xPosition)

    def redraw(self, frame, *fargs):
        '''
        Redraws the graph based on the yPosition.
        '''
        curveData, curveIdx = self.findNearestXYData()
        if curveIdx != -1:
            colour = self._chart.getColour(curveIdx, len(self._measurementModel))
            self._pressure_curve.set_ydata(curveData.y)
            self._pressure_curve.set_color(colour)
            idx = self.__find_nearest_xy(curveData)
            self._pressure_marker.set_data(curveData.x[idx], curveData.y[idx])
            self.__marker_data.freq = curveData.x[idx]
            self.__marker_data.spl = curveData.y[idx]
            self._pressure_marker.set_color(colour)
            self._vline.set_xdata([curveData.x[idx], curveData.x[idx]])
        return self._pressure_curve, self._pressure_marker, self._vline

    def findNearestXYData(self):
        '''
        Searches the available data to find the curve that is the closest hAngle to our current yPosition.
        :return: (curveIdx, curveData) or (-1, None) if nothing is found.
        '''
        curveIdx = -1
        curveData = None
        delta = 100000000
        if self.yPosition is not None:
            for idx, x in enumerate(self._pressure_data):
                newDelta = abs(self.yPosition - x.hAngle)
                if newDelta < delta:
                    delta = newDelta
                    curveIdx = idx
                    curveData = x
                elif newDelta > delta:
                    break
        return curveData, curveIdx

    def onUpdate(self, type, **kwargs):
        '''
        handles measurement model changes
        If event type is activation toggle then changes the associated curve visibility.
        If event type is analysis change then the model is marked for refresh.
        :param idx: the measurement idx.
        '''
        if type == LOAD_MEASUREMENTS:
            self._refreshData = True
        elif type == CLEAR_MEASUREMENTS:
            self.clear()

    def clear(self, draw=True):
        '''
        clears the graph.
        '''
        self.stop_animation()
        self._axes.clear()
        self._pressure_curve = None
        formatAxes_dBFS_Hz(self._axes)
        if draw:
            self._chart.canvas.draw_idle()

    def stop_animation(self):
        '''
        Stops the animation.
        '''
        if self._ani is not None:
            logger.info(f"Stopping animation in {self.name}")
            ani = self._ani
            self._ani = None
            self._refreshData = True
            ani._stop()
