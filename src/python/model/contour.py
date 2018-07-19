import numpy as np

from model import configureFreqAxisFormatting
from model.measurement import CLEAR_MEASUREMENTS, ANALYSED


class ContourModel:
    '''
    Allows a set of FRs to be displayed as a directivity sonargram.
    '''

    def __init__(self, chart, measurementModel, contourInterval, type):
        self._chart = chart
        self._axes = None
        self._initChart()
        self._measurementModel = measurementModel
        self._selectedCmap = 'plasma'
        self._contourInterval = contourInterval
        self._type = type
        self._data = None
        self._tc = None
        self._tcf = None
        self._refreshData = False
        self._measurementModel.registerListener(self)

    def shouldRefresh(self):
        return self._refreshData

    def _initChart(self):
        '''
        Initialises the chart with the default configuration.
        '''
        self._axes = self._chart.canvas.figure.add_subplot(111)
        self._axes.axis('auto')
        self._axes.set_xscale('log')
        self._axes.set_xlabel('Hz')
        self._axes.set_ylabel('Degrees')
        self._axes.grid(linestyle='-', which='major', linewidth=1, alpha=0.5)
        self._axes.grid(linestyle='--', which='minor', linewidth=1, alpha=0.5)

    def onUpdate(self, type, **kwargs):
        '''
        Handles events from the measurement model.
        :param type: the type.
        :param kwargs: any additional args.
        :return:
        '''
        if type == ANALYSED:
            self._refreshData = True
        elif type == CLEAR_MEASUREMENTS:
            self.clear()

    def display(self):
        '''
        Updates the contents of the chart.
        '''
        if self._refreshData and len(self._measurementModel) > 0:
            self._data = self._measurementModel.getContourData(type=self._type)
            self._extents = [np.amin(self._data['x']), np.amax(self._data['x']),
                             np.amax(self._data['y']), np.amin(self._data['y'])]
            vmax = np.math.ceil(np.amax(self._data['z']))
            vmin = np.math.floor(np.amin(self._data['z']))

            if self._tcf:
                self.clear()
            steps = np.flip(np.concatenate(([vmax-2, vmax-4], np.arange(vmax-6, vmin, -6))), 0)
            self._tc = self._axes.tricontour(self._data['x'], self._data['y'], self._data['z'], steps, linewidths=0.5,
                                             colors='k')
            self._tcf = self._axes.tricontourf(self._data['x'], self._data['y'], self._data['z'], steps,
                                               cmap=self._chart.getColourMap(self._selectedCmap))
            self._cb = self._chart.canvas.figure.colorbar(self._tcf)
            configureFreqAxisFormatting(self._axes)
            self._tcf.set_clim(vmin=vmin, vmax=vmax)
            self._chart.canvas.draw()
            self._refreshData = False

    def updateColourMap(self, cmap):
        '''
        Updates the currently selected colour map.
        :param cmap: the cmap name.
        '''
        if self._tcf:
            self._tcf.set_cmap(cmap)
            self._chart.canvas.draw()
        self._selectedCmap = cmap

    def clear(self):
        '''
        clears the graph.
        '''
        if self._tcf:
            self._chart.canvas.figure.clear()
            self._initChart()
            self._chart.canvas.draw()
            self._tc = None
            self._tcf = None

    def updateContourInterval(self, interval):
        '''
        Redraws with a new contour interval.
        :param interval: the interval
        '''
        self._contourInterval = interval
        self._refreshData = True
        self.display()
