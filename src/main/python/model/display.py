class DisplayModel:
    '''
    Parameters to feed into how a chart should be displayed.
    '''

    def __init__(self, dBRange=60, normalised=False, normalisationAngle=0, visibleChart=None):
        self.__dBRange = dBRange
        self.__normalised = normalised
        self.__normalisationAngle = normalisationAngle
        self.__visibleChart = visibleChart
        self.resultCharts = []
        self.measurementModel = None

    def __repr__(self):
        return self.__class__.__name__

    @property
    def dBRange(self):
        return self.__dBRange

    @dBRange.setter
    def dBRange(self, dBRange):
        self.__dBRange = dBRange
        for chart in self.resultCharts:
            chart.updateDecibelRange(self.__dBRange, draw=chart is self.__visibleChart)

    @property
    def normalised(self):
        return self.__normalised

    @normalised.setter
    def normalised(self, normalised):
        self.__normalised = normalised
        self.measurementModel.normalisationChanged()
        self.__redrawVisible()

    @property
    def normalisationAngle(self):
        return self.__normalisationAngle

    @normalisationAngle.setter
    def normalisationAngle(self, normalisationAngle):
        changed = normalisationAngle != self.__normalisationAngle
        self.__normalisationAngle = normalisationAngle
        if changed and self.__normalised:
            self.measurementModel.normalisationChanged()
            self.__redrawVisible()

    @property
    def visibleChart(self):
        return self.__visibleChart

    @visibleChart.setter
    def visibleChart(self, visibleChart):
        self.__visibleChart = visibleChart
        self.__redrawVisible()

    def __redrawVisible(self):
        if self.__visibleChart is not None:
            display = getattr(self.__visibleChart, 'display', None)
            if display is not None and callable(display):
                display()
