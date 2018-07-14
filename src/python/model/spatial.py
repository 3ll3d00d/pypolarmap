import numpy as np


class SpatialModel:
    '''
    Does something but I don't know what
    '''

    def __init__(self, chart, measurementModel, measurementDistance, driverRadius, modalCoeffs, f0, q0, transFreq,
                 lfGain, boxRadius):
        self.__boxRadius = boxRadius
        self.__lfGain = lfGain
        self.__transFreq = transFreq
        self.__q0 = q0
        self.__f0 = f0
        self.__modalCoeffs = modalCoeffs
        self.__driverRadius = driverRadius
        self.__measurementDistance = measurementDistance
        self.__chart = chart
        self.__axes = None
        self._initChart()
        self.__measurementModel = measurementModel
        self.__refreshData = False
        self.__tcf = None
        self.__tc = None

    @property
    def measurementDistance(self):
        return self.__measurementDistance

    @measurementDistance.setter
    def measurementDistance(self, measurementDistance):
        self.__measurementDistance = measurementDistance
        self.__refreshData = True

    @property
    def driverRadius(self):
        return self.__driverRadius

    @driverRadius.setter
    def driverRadius(self, driverRadius):
        self.__driverRadius = driverRadius
        self.__refreshData = True

    @property
    def modalCoeffs(self):
        return self.__modalCoeffs

    @modalCoeffs.setter
    def modalCoeffs(self, modalCoeffs):
        self.__modalCoeffs = modalCoeffs
        self.__refreshData = True

    @property
    def f0(self):
        return self.__f0

    @f0.setter
    def f0(self, f0):
        self.__f0 = f0
        self.__refreshData = True

    @property
    def q0(self):
        return self.__q0

    @q0.setter
    def q0(self, q0):
        self.__q0 = q0
        self.__refreshData = True

    @property
    def transFreq(self):
        return self.__transFreq

    @transFreq.setter
    def transFreq(self, transFreq):
        self.__transFreq = transFreq
        self.__refreshData = True

    @property
    def lfGain(self):
        return self.__lfGain

    @lfGain.setter
    def lfGain(self, lfGain):
        self.__lfGain = lfGain
        self.__refreshData = True

    @property
    def boxRadius(self):
        return self.__boxRadius

    @boxRadius.setter
    def boxRadius(self, boxRadius):
        self.__boxRadius = boxRadius
        self.__refreshData = True

    def _initChart(self):
        '''
        Initialises the chart with the default configuration.
        '''
        self.__axes = self.__chart.canvas.figure.add_subplot(111)
        self.__axes.axis('auto')
        self.__axes.set_xscale('log')

    def markForRefresh(self):
        '''
        Marks this model as in need of recalculation.
        '''
        self.__refreshData = True

    def display(self):
        '''
        Updates the contents of the chart.
        '''
        if self.__refreshData and len(self.__measurementModel) > 0:
            self.__measurementModel.calSpatial(self.__measurementDistance, self.__driverRadius, self.__modalCoeffs,
                                               self.__transFreq, self.__lfGain, self.__boxRadius, self.__f0, self.__q0)
            # convert to a table of xyz coordinates where x = frequencies, y = angles, z = magnitude
            self._x = np.array([x.logFreqs for x in self.__measurementModel]).flatten()
            self._y = np.array([x._h for x in self.__measurementModel]).repeat(self.__measurementModel[0].logFreqs.size)
            self._z = self.__measurementModel.spatialMagnitude().flatten()
            self._extents = [np.amin(self._x), np.amax(self._x), np.amax(self._y), np.amin(self._y)]
            vmax = np.math.ceil(np.amax(self._z))
            vmin = np.math.floor(np.amin(self._z))

            if self.__tcf:
                self.clear()

            steps = np.flip(np.arange(vmax, vmin, -6), 0)
            self.__tc = self.__axes.tricontour(self._x, self._y, self._z, 18, linewidths=0.5, colors='k')
            self.__tcf = self.__axes.tricontourf(self._x, self._y, self._z, 18,
                                                 cmap=self.__chart.getColourMap('plasma'))
            self._cb = self.__chart.canvas.figure.colorbar(self.__tcf)
            self.__tcf.set_clim(vmin=vmin, vmax=vmax)
            self.__chart.canvas.draw()
            self.__refreshData = False

    def clear(self):
        '''
        clears the graph.
        '''
        if self.__tcf:
            self.__chart.canvas.figure.clear()
            self._initChart()
            self.__chart.canvas.draw()
            self.__tc = None
            self.__tcf = None
