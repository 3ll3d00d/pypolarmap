import numpy as np

from model import configureFreqAxisFormatting


class PolarModel:
    '''
    Allows a set of FRs to be displayed as a directivity sonargram.
    '''

    def __init__(self, chart, measurementModel, spatialModel, contourInterval):
        self._chart = chart
        self._axes = None
        self._initChart()
        self._measurementModel = measurementModel
        self._spatialModel = spatialModel
        self._selectedCmap = 'plasma'
        self._contourInterval = contourInterval
        self._x = None
        self._y = None
        self._z = None
        self._tc = None
        self._tcf = None
        self._refreshData = False

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

    def markForRefresh(self):
        '''
        Marks this model as in need of recalculation.
        '''
        self._refreshData = True
        self._spatialModel.markForRefresh()

    def display(self):
        '''
        Updates the contents of the chart.
        '''
        if self._refreshData and len(self._measurementModel) > 0:
            # convert to a table of xyz coordinates where x = frequencies, y = angles, z = magnitude
            self._x = np.array([x.logFreqs for x in self._measurementModel]).flatten()
            self._y = np.array([x._h for x in self._measurementModel]).repeat(self._measurementModel[0].logFreqs.size)
            self._z = np.array([x.getMagnitude(ref=1) for x in self._measurementModel]).flatten()
            self._extents = [np.amin(self._x), np.amax(self._x), np.amax(self._y), np.amin(self._y)]
            vmax = np.math.ceil(np.amax(self._z))
            vmin = np.math.floor(np.amin(self._z))

            if self._tcf:
                self.clear()

            steps = np.flip(np.arange(vmax, vmin, -self._contourInterval), 0)
            self._tc = self._axes.tricontour(self._x, self._y, self._z, steps, linewidths=0.5, colors='k')
            self._tcf = self._axes.tricontourf(self._x, self._y, self._z, steps,
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
        self.markForRefresh()
        self.display()
