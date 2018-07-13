from math import log10

import numpy as np


def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


majorFreq = [20, 100, 1000, 10000, 20000]
minorFreq = [30, 40, 50, 200, 300, 400, 500, 2000, 3000, 4000, 5000, 20000]

freqTicks = [
    [(log10(x), human_format(x)) for x in majorFreq],
    [(log10(x), human_format(x)) for x in minorFreq],
]


class MagnitudeModel:
    '''
    Allows a set of measurements to be displayed on a chart as magnitude responses.
    '''

    def __init__(self, chart, measurementModel, polar):
        self._chart = chart
        self._axes = self._chart.canvas.figure.add_subplot(111)
        self._axes.set_xlim(left=20, right=20000)
        # TODO format xticks, add grid
        self._axes.grid()
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
