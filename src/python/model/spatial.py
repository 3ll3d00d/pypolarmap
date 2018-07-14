class SpatialModel:
    '''
    Does something but I don't know what
    '''

    def __init__(self, chart, measurementModel, measurementDistance, driverRadius, modalCoeffs, f0, q0, transFreq,
                 lfGain, boxRadius):
        self.boxRadius = boxRadius
        self.lfGain = lfGain
        self.transFreq = transFreq
        self.q0 = q0
        self.f0 = f0
        self.modalCoeffs = modalCoeffs
        self.driverRadius = driverRadius
        self.measurementDistance = measurementDistance
        self._chart = chart
        self._axes = None
        self._initChart()
        self._measurementModel = measurementModel
        self._refreshData = False

    def _initChart(self):
        '''
        Initialises the chart with the default configuration.
        '''
        self._axes = self._chart.canvas.figure.add_subplot(111)

    def markForRefresh(self):
        '''
        Marks this model as in need of recalculation.
        '''
        self._refreshData = True

    def display(self):
        '''
        Updates the contents of the chart.
        '''
        if self._refreshData and len(self._measurementModel) > 0:
            self._measurementModel.calSpatial(self.measurementDistance, self.driverRadius, self.modalCoeffs,
                                              self.transFreq, self.lfGain, self.boxRadius, self.f0, self.q0)
            self._refreshData = False

    def clear(self):
        '''
        clears the graph.
        '''
        pass
        # if self._tcf:
        #     self._chart.canvas.figure.clear()
        #     self._initChart()
        #     self._chart.canvas.draw()
        #     self._tc = None
        #     self._tcf = None
