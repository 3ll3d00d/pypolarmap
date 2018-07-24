import numpy as np
from matplotlib import animation

from model import configureFreqAxisFormatting, formatAxes_dBFS_Hz, setYLimits, SINGLE_SUBPLOT_SPEC, \
    calculate_dBFS_Scales
from model.measurement import REAL_WORLD_DATA, ANALYSED, CLEAR_MEASUREMENTS, LOAD_MEASUREMENTS


class MagnitudeModel:
    '''
    Allows a set of measurements to be displayed on a chart as magnitude responses.
    '''

    def __init__(self, chart, measurementModel, type=REAL_WORLD_DATA, modelListener=None,
                 subplotSpec=SINGLE_SUBPLOT_SPEC, showLegend=True, dBRange=60):
        self._chart = chart
        self._axes = self._chart.canvas.figure.add_subplot(subplotSpec)
        formatAxes_dBFS_Hz(self._axes)
        self._curves = {}
        self._refreshData = False
        self._type = type
        self._measurementModel = measurementModel
        self._modelListener = modelListener
        self._showLegend = showLegend
        self._measurementModel.registerListener(self)
        self._dBRange = dBRange
        self.updateDecibelRange(self._dBRange, draw=False)

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
            self._chart.canvas.draw()

    def display(self):
        '''
        Updates the contents of the magnitude chart
        '''
        # TODO might need to update the ylim even if we haven't refreshed
        if self.shouldRefresh():
            data = self._measurementModel.getMagnitudeData(type=self._type, ref=1)
            for idx, x in enumerate(data):
                curve = self._curves.get(x.name)
                if curve:
                    curve.set_data(x.x, x.y)
                else:
                    # todo consider making the reference user selectable, e.g. to allow for dB SPL output
                    self._curves[x.name] = self._axes.semilogx(x.x, x.y,
                                                               linewidth=2,
                                                               antialiased=True,
                                                               linestyle='solid',
                                                               color=self._chart.getColour(idx,
                                                                                           len(self._measurementModel)),
                                                               label=x.name)[0]
            configureFreqAxisFormatting(self._axes)
            ymax, ymin, _, _ = calculate_dBFS_Scales(np.concatenate([x.y for x in data]), maxRange=self._dBRange)
            self._axes.set_ylim(bottom=ymin, top=ymax)
            if self._axes.get_legend() is None and self._showLegend:
                self.makeClickableLegend()
            self._chart.canvas.draw()
            self._refreshData = False
        else:
            ylim = self._axes.get_ylim()
            if ylim[1] - ylim[0] != self._dBRange:
                self.updateDecibelRange(self._dBRange)

    def makeClickableLegend(self):
        '''
        Add a legend that allows you to make a line visible or invisible by clicking on it.
        ripped from https://matplotlib.org/2.0.0/examples/event_handling/legend_picking.html
        and https://stackoverflow.com/questions/4700614/how-to-put-the-legend-out-of-the-plot
        '''
        # box = self._axes.get_position()
        # self._axes.set_position([box.x0, box.y0 + box.height * 0.2, box.width, box.height * 0.8])
        # # Put a legend below current axis
        # legend = self._axes.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fancybox=True, shadow=True, ncol=5)
        legend = self._axes.legend(loc='best', fancybox=True, shadow=True)
        lined = dict()
        for legline, origline in zip(legend.get_lines(), self._curves.values()):
            legline.set_picker(5)  # 5 pts tolerance
            lined[legline] = origline

        def onpick(event):
            # on the pick event, find the orig line corresponding to the legend proxy line, and toggle the visibility
            legline = event.artist
            origline = lined[legline]
            vis = not origline.get_visible()
            origline.set_visible(vis)
            # Change the alpha on the line in the legend so we can see what lines have been toggled
            if vis:
                legline.set_alpha(1.0)
            else:
                legline.set_alpha(0.2)
            self._chart.canvas.draw()
        self._chart.canvas.mpl_connect('pick_event', onpick)

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


class AnimatedSingleLineMagnitudeModel:
    '''
    Allows a single measurement from a selection of magnitude data to be displayed on a chart.
    '''

    def __init__(self, chart, measurementModel, type=REAL_WORLD_DATA, subplotSpec=SINGLE_SUBPLOT_SPEC, dBRange=60):
        self._chart = chart
        self._measurementModel = measurementModel
        self._measurementModel.registerListener(self)
        self._axes = self._chart.canvas.figure.add_subplot(subplotSpec)
        formatAxes_dBFS_Hz(self._axes)
        self._type = type
        self._refreshData = False
        self._type = type
        self.yPosition = None
        self._curve = None
        self._ani = None
        self._dBRange = dBRange

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
            self._chart.canvas.draw()

    def display(self):
        '''
        Gets fresh data and redraws
        '''
        if self.shouldRefresh():
            if self._curve is None:
                self._data = self._measurementModel.getMagnitudeData(type=self._type, ref=1)
                self._curve = self._axes.semilogx(self._data[0].x,
                                                  [np.nan] * len(self._data[0].x),
                                                  linewidth=2,
                                                  antialiased=True,
                                                  linestyle='solid')[0]
                yMax = max([np.max(x.y) for x in self._data])
                yMin = yMax - self._dBRange
                self._axes.set_ylim(bottom=yMin, top=yMax, auto=False)
                self._ani = animation.FuncAnimation(self._chart.canvas.figure, self.redraw, interval=50,
                                                    init_func=self.initAnimation, blit=True, save_count=50)
                configureFreqAxisFormatting(self._axes)
                self._refreshData = False

    def initAnimation(self):
        '''
        Inits a blank screen.
        :return: the curve artist.
        '''
        self._curve.set_ydata([np.nan] * len(self._data[0].x))
        return self._curve,

    def redraw(self, frame, *fargs):
        '''
        Redraws the graph based on the yPosition.
        '''
        curveData, curveIdx = self.findNearestXYData()
        if curveIdx != -1:
            self._curve.set_ydata(curveData.y)
            self._curve.set_color(self._chart.getColour(curveIdx, len(self._measurementModel)))
        return self._curve,

    def findNearestXYData(self):
        '''
        Searches the available data to find the curve that is the closest hAngle to our current yPosition.
        :return: (curveIdx, curveData) or (-1, None) if nothing is found.
        '''
        curveIdx = -1
        curveData = None
        delta = 100000000
        if self.yPosition is not None:
            for idx, x in enumerate(self._data):
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
        self._curve = None
        self._ani = None
