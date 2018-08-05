import math

import numpy as np
from matplotlib import animation
from matplotlib.ticker import MultipleLocator, FuncFormatter

from model import calculate_dBFS_Scales, SINGLE_SUBPLOT_SPEC, setYLimits
from model.measurement import REAL_WORLD_DATA, ANALYSED, LOAD_MEASUREMENTS, CLEAR_MEASUREMENTS


class PolarModel:
    '''
    Allows a set of measurements to be displayed on a polar chart with the displayed curve interactively changing.
    '''

    def __init__(self, chart, measurementModel, type=REAL_WORLD_DATA, subplotSpec=SINGLE_SUBPLOT_SPEC,
                 redrawOnDisplay=True, dBRange=60):
        self._chart = chart
        self._axes = self._chart.canvas.figure.add_subplot(subplotSpec, projection='polar')
        self._axes.grid(linestyle='--', axis='y', alpha=0.7)
        self._data = {}
        self._curve = None
        self._refreshData = False
        self._type = type
        self.name = f"polar_{self._type}"
        self._measurementModel = measurementModel
        self._measurementModel.registerListener(self)
        self.xPosition = 1000
        self._ani = None
        self._redrawOnDisplay = redrawOnDisplay
        self._dBRange = dBRange
        self._y_range_update_required = False
        self.updateDecibelRange(self._dBRange, draw=False)

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
        if self._ani:
            # have to clear the blit cache to get the r grid to redraw as per
            # https://stackoverflow.com/questions/25021311/matplotlib-animation-updating-radial-view-limit-for-polar-plot
            self._ani._blit_cache.clear()
        if draw:
            self._chart.canvas.draw()
            self._y_range_update_required = False

    def display(self):
        '''
        Updates the contents of the polar chart.
        :return: true if it redrew.
        '''
        if self.shouldRefresh():
            # convert x-y by theta data to theta-r by freq
            xydata = self._measurementModel.getMagnitudeData(type=self._type, ref=1)
            self._data = {}
            for idx, freq in enumerate(xydata[0].x):
                theta, r = zip(*[(math.radians(x.hAngle), x.y[idx]) for x in xydata])
                self._data[freq] = (theta, r)
            self._axes.set_thetagrids(np.arange(0, 360, 15))
            rmax, rmin, rsteps, _ = calculate_dBFS_Scales(np.concatenate([x[1] for x in self._data.values()]),
                                                          maxRange=self._dBRange)
            self._axes.set_rgrids(rsteps)
            # show degrees as +/- 180
            self._axes.xaxis.set_major_formatter(FuncFormatter(self.formatAngle))
            # show label every 12dB
            self._axes.yaxis.set_major_locator(MultipleLocator(12))
            # plot some invisible data to initialise
            self._curve = self._axes.plot([math.radians(-180), math.radians(180)], [-200, -200], linewidth=2,
                                          antialiased=True, linestyle='solid', visible=False)[0]
            self._axes.set_ylim(bottom=rmin, top=rmax)
            self._ani = animation.FuncAnimation(self._chart.canvas.figure, self.redraw, interval=50,
                                                init_func=self.initAnimation, blit=True, save_count=50)
            self._y_range_update_required = False
            self._refreshData = False
            return True
        else:
            if self._axes is not None and self._y_range_update_required:
                self.updateDecibelRange(self._dBRange, self._redrawOnDisplay)
        return False

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
