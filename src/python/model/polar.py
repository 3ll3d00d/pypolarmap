import math

import numpy as np
from matplotlib import animation
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MultipleLocator, FuncFormatter

from model import calculate_dBFS_Scales
from model.measurement import REAL_WORLD_DATA, ANALYSED, LOAD_MEASUREMENTS, CLEAR_MEASUREMENTS


class PolarModel:
    '''
    Allows a set of measurements to be displayed on a polar chart with the displayed curve interactively changing.
    '''

    def __init__(self, chart, measurementModel, type=REAL_WORLD_DATA,
                 subplotSpec=GridSpec(1, 1).new_subplotspec((0, 0), 1, 1)):
        self._chart = chart
        self._axes = self._chart.canvas.figure.add_subplot(subplotSpec, projection='polar')
        self._axes.grid(linestyle='--', axis='y', alpha=0.7)
        self._data = {}
        self._curve = None
        self._refreshData = False
        self._type = type
        self._measurementModel = measurementModel
        self._measurementModel.registerListener(self)
        self.xPosition = 1000
        self._ani = None

    def shouldRefresh(self):
        return self._refreshData

    def display(self):
        '''
        Updates the contents of the magnitude chart
        '''
        if self.shouldRefresh():
            # convert x-y by theta data to theta-r by freq
            xydata = self._measurementModel.getMagnitudeData(type=self._type, ref=1)
            self._data = {}
            for idx, freq in enumerate(xydata[0].x):
                theta, r = zip(*[(math.radians(x.hAngle), x.y[idx]) for x in xydata])
                self._data[freq] = (theta, r)
            self._axes.set_thetagrids(np.arange(0, 360, 15))
            rmax, rmin, rsteps = calculate_dBFS_Scales(np.concatenate([x[1] for x in self._data.values()]))
            self._axes.set_rgrids(rsteps)
            # show degrees as +/- 180
            self._axes.xaxis.set_major_formatter(FuncFormatter(self.formatAngle))
            # self._axes.set_xticklabels(np.concatenate((np.arange(0, 195, 15), np.arange(-165, 0, 15))))
            # show label every 12dB
            self._axes.yaxis.set_major_locator(MultipleLocator(12))
            # plot some invisible data to initialise
            self._curve = self._axes.plot([math.radians(-180), math.radians(180)], [-200, -200], linewidth=2,
                                          antialiased=True, linestyle='solid', visible=False)[0]
            self._axes.set_ylim(bottom=rmin, top=rmax)
            self._ani = animation.FuncAnimation(self._chart.canvas.figure, self.redraw, interval=50,
                                                init_func=self.initAnimation, blit=True, save_count=50)
            self._refreshData = False

    def formatAngle(self, x, pos=None):
        format_str = "{value:0.{digits:d}f}\N{DEGREE SIGN}"
        deg = np.rad2deg(x)
        if deg > 180:
            deg = deg - 360
        return format_str.format(value=deg, digits=0)

    def initAnimation(self):
        '''
        Inits a blank screen.
        :return: the curve artist.
        '''
        self._curve.set_ydata([-200, -200])
        return self._curve,

    def redraw(self, frame, *fargs):
        '''
        Redraws the graph based on the yPosition.
        '''
        curveIdx, curveData = self.findNearestData()
        if curveIdx != -1:
            self._curve.set_visible(True)
            self._curve.set_xdata(curveData[0])
            self._curve.set_ydata(curveData[1])
            self._curve.set_color(self._chart.getColour(curveIdx, len(self._data.keys())))
        return self._curve,

    def findNearestData(self):
        '''
        Searches the available data to find the curve that is the closest freq to our current xPosition.
        :return: (curveIdx, curveData) or (-1, None) if nothing is found.
        '''
        curveIdx = -1
        curveData = None
        delta = 100000000
        for idx, (freq, v) in enumerate(self._data.items()):
            newDelta = abs(self.xPosition - freq)
            if newDelta < delta:
                delta = newDelta
                curveIdx = idx
                curveData = v
            elif newDelta > delta:
                break
        return curveIdx, curveData

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
        self._data = {}
        self._curve = None
        self._ani = None
