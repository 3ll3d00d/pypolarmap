from matplotlib.ticker import EngFormatter

from model import PrintFirstHalfFormatter, configureFreqAxisFormatting


class MagnitudeModel:
    '''
    Allows a set of measurements to be displayed on a chart as magnitude responses.
    '''

    def __init__(self, chart, measurementModel, polar):
        self._chart = chart
        self._axes = self._chart.canvas.figure.add_subplot(111)
        self._axes.set_xlim(left=20, right=20000)
        self._axes.grid(linestyle='-', which='major')
        self._axes.grid(linestyle='--', which='minor')
        self._axes.set_ylabel('dBFS')
        self._axes.set_xlabel('Hz')
        self._curves = {}
        self._polarModel = polar
        self._refreshData = False
        self._measurementModel = measurementModel
        self._measurementModel.registerListener(self)

    def markForRefresh(self):
        '''
        Marks this model as in need of recalculation.
        '''
        self._refreshData = True
        self._polarModel.markForRefresh()

    def display(self):
        '''
        Updates the contents of the magnitude chart
        '''
        if self._refreshData:
            for idx, x in enumerate(self._measurementModel):
                curve = self._curves.get(x.getDisplayName())
                if curve:
                    curve.set_data(x.logFreqs, x.getMagnitude(ref=1))
                else:
                    # todo consider making the reference user selectable, e.g. to allow for dB SPL output
                    self._curves[x.getDisplayName()] = self._axes.semilogx(x.logFreqs, x.getMagnitude(ref=1),
                                                                           linewidth=2, antialiased=True,
                                                                           linestyle='solid',
                                                                           color=self._chart.getColour(idx),
                                                                           visible=x._active)[0]
            configureFreqAxisFormatting(self._axes)
            self._chart.canvas.draw()
            self._refreshData = False

    def onMeasurementUpdate(self, idx=None):
        '''
        toggles the measurement on and off.
        :param idx: the measurement idx.
        :return:
        '''
        if idx is None:
            pass
        else:
            m = self._measurementModel[idx] if idx < len(self._measurementModel) else None
            if m:
                curve = self._curves.get(m.getDisplayName())
                if curve:
                    curve.set_visible(m._active)
                    self._chart.canvas.draw()

    def clear(self):
        '''
        clears the graph.
        '''
        self._axes.clear()
        self._curves = {}
