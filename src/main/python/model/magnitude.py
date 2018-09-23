import numpy as np
from matplotlib import animation
from qtpy.QtWidgets import QListWidgetItem

from model import configureFreqAxisFormatting, formatAxes_dBFS_Hz, setYLimits, SINGLE_SUBPLOT_SPEC, \
    calculate_dBFS_Scales
from model.measurement import REAL_WORLD_DATA, ANALYSED, CLEAR_MEASUREMENTS, LOAD_MEASUREMENTS


class MagnitudeModel:
    '''
    Allows a set of measurements to be displayed on a chart as magnitude responses.
    '''

    def __init__(self, chart, measurementModel, display_model, type=REAL_WORLD_DATA, modelListener=None,
                 subplotSpec=SINGLE_SUBPLOT_SPEC, showLegend=True, selector=None):
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
        self._dBRange = display_model.dBRange
        self._selector = selector
        if self._selector is not None:
            self._selector.itemSelectionChanged.connect(self.set_visible)
        self.updateDecibelRange(self._dBRange, draw=False)

    def set_visible(self):
        ''' ensures the visible curves tracks the contents of the selector '''
        selected = [x.text() for x in self._selector.selectedItems()]
        for name, curve in self._curves.items():
            curve.set_visible(name in selected)
        self._chart.canvas.draw_idle()

    def __repr__(self):
        return self.name

    def shouldRefresh(self):
        return self._refreshData

    def updateDecibelRange(self, dBRange, draw=True):
        '''
        Updates the decibel range on the chart.
        :param dBRange: the new range.
        '''
        self._dBRange = dBRange
        if draw:
            setYLimits(self._axes, dBRange)
            self._chart.canvas.draw_idle()

    def display(self):
        '''
        Updates the contents of the magnitude chart
        '''
        # TODO might need to update the ylim even if we haven't refreshed
        if self.shouldRefresh():
            # magnitude data on primary axis
            data = self._measurementModel.getMagnitudeData(type=self._type, ref=1)
            for idx, x in enumerate(data):
                self._create_or_update_curve(x, self._axes, self._chart.getColour(idx, len(self._measurementModel)))
            self._update_y_lim(np.concatenate([x.y for x in data]), self._axes)

            # power data on secondary axis
            power = self._measurementModel.getPowerResponse(type=self._type, ref=1)
            if power is not None:
                self._create_or_update_curve(power, self._axes, 'k')
                self._update_y_lim(power.y, self._axes)

            if self._axes.get_legend() is None and self._showLegend:
                lines = self._curves.values()
                self._axes.legend(lines, [l.get_label() for l in lines], loc=8, ncol=4, fancybox=True, shadow=True)
            if self._selector is not None:
                self._selector.selectAll()
            else:
                self._chart.canvas.draw_idle()
            self._refreshData = False
        else:
            ylim = self._axes.get_ylim()
            if ylim[1] - ylim[0] != self._dBRange:
                self.updateDecibelRange(self._dBRange)

    def _update_y_lim(self, data, axes):
        configureFreqAxisFormatting(axes)
        ymax, ymin, _, _ = calculate_dBFS_Scales(data, maxRange=self._dBRange)
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
        if type == ANALYSED or type == LOAD_MEASUREMENTS:
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

    def __init__(self, chart, measurementModel, display_model, type=REAL_WORLD_DATA, subplotSpec=SINGLE_SUBPLOT_SPEC,
                 redrawOnDisplay=True):
        self._chart = chart
        self._measurementModel = measurementModel
        self._measurementModel.registerListener(self)
        self._axes = self._chart.canvas.figure.add_subplot(subplotSpec)
        self._power_axes = self._axes.twinx()
        formatAxes_dBFS_Hz(self._axes)
        self._type = type
        self.name = f"single-magnitude_{type}"
        self._refreshData = False
        self._type = type
        self.yPosition = None
        self._pressure_data = None
        self._pressure_curve = None
        self._power_data = None
        self._power_curve = None
        self._di_curve = None
        self._ani = None
        self._y_range_update_required = False
        self._redrawOnDisplay = redrawOnDisplay
        self._dBRange = display_model.dBRange

    def __repr__(self):
        return self.name

    def shouldRefresh(self):
        return self._refreshData

    def updateDecibelRange(self, dBRange, draw=True):
        '''
        Updates the decibel range on the chart.
        :param dBRange: the new range.
        '''
        self._dBRange = dBRange
        self._y_range_update_required = True
        setYLimits(self._axes, dBRange)
        setYLimits(self._power_axes, dBRange)
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
        if self.shouldRefresh():
            if self._pressure_curve is None:
                # pressure
                self._pressure_data = self._measurementModel.getMagnitudeData(type=self._type, ref=1)
                self._pressure_curve = self._axes.semilogx(self._pressure_data[0].x,
                                                           [np.nan] * len(self._pressure_data[0].x),
                                                           linewidth=2,
                                                           antialiased=True,
                                                           linestyle='solid')[0]
                ymax, ymin, _, _ = calculate_dBFS_Scales(np.concatenate([x.y for x in self._pressure_data]),
                                                         maxRange=self._dBRange)
                self._axes.set_ylim(bottom=ymin, top=ymax, auto=False)
                # directivity
                self._di_curve = self._axes.semilogx(self._pressure_data[0].x,
                                                     [np.nan] * len(self._pressure_data[0].x),
                                                     linewidth=2,
                                                     antialiased=True,
                                                     linestyle='--')[0]
                # power
                self._power_data = self._measurementModel.getPowerResponse(type=self._type, ref=1)
                self._power_curve = self._power_axes.semilogx(self._power_data.x,
                                                              self._power_data.y,
                                                              linewidth=2,
                                                              antialiased=True,
                                                              color='k',
                                                              linestyle='solid')[0]
                ymax, ymin, _, _ = calculate_dBFS_Scales(self._power_data.y, maxRange=self._dBRange)
                self._power_axes.set_ylim(bottom=ymin, top=ymax, auto=False)

                self._ani = animation.FuncAnimation(self._chart.canvas.figure, self.redraw, interval=50,
                                                    init_func=self.initAnimation, blit=True, save_count=50)
                configureFreqAxisFormatting(self._axes)
                self._y_range_update_required = False
                self._refreshData = False
                return True
        else:
            if self._pressure_curve is not None:
                if self._y_range_update_required:
                    self.updateDecibelRange(self._dBRange, self._redrawOnDisplay)
                if self._ani is None:
                    self._ani = animation.FuncAnimation(self._chart.canvas.figure, self.redraw, interval=50,
                                                        init_func=self.initAnimation, blit=True, save_count=50)
        return False

    def initAnimation(self):
        '''
        Inits a blank screen.
        :return: the curve artist.
        '''
        self._pressure_curve.set_ydata([np.nan] * len(self._pressure_data[0].x))
        return self._pressure_curve, self._power_curve, self._di_curve

    def redraw(self, frame, *fargs):
        '''
        Redraws the graph based on the yPosition.
        '''
        curveData, curveIdx = self.findNearestXYData()
        if curveIdx != -1:
            colour = self._chart.getColour(curveIdx, len(self._measurementModel))
            self._pressure_curve.set_ydata(curveData.y)
            self._pressure_curve.set_color(colour)
            self._di_curve.set_ydata((curveData.y * curveData.y) / self._power_data.y)
            self._di_curve.set_color(colour)
        return self._pressure_curve, self._power_curve, self._di_curve

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
        if type == ANALYSED or type == LOAD_MEASUREMENTS:
            self._refreshData = True
        elif type == CLEAR_MEASUREMENTS:
            self.clear()

    def clear(self):
        '''
        clears the graph.
        '''
        self._axes.clear()
        self._pressure_curve = None
        self.stop_animation()

    def stop_animation(self):
        '''
        Stops the animation.
        '''
        if self._ani is not None:
            self._ani._stop()
            self._ani = None
            self._refreshData = True
