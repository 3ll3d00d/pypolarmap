from math import log10

import pyqtgraph as pg
import numpy as np

from meascalcs import fft, linToLog


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


class MagnitudeWidget(pg.PlotWidget):
    '''
    Extends PlotWidget because there is way to set an axis after the widget is created and no way to pass custom
    constructors via qtdesigner.
    '''

    def __init__(self, parent):
        super(MagnitudeWidget, self).__init__(parent=parent)
        self.getPlotItem().getAxis('bottom').setTicks(freqTicks)
        self.getPlotItem().getAxis('bottom').setLabel(text='Freq', units='Hz')
        self.getPlotItem().getAxis('left').setLabel(text='dB')
        self.getPlotItem().setLogMode(x=True, y=False)
        self.getPlotItem().showGrid(x=True, y=True, alpha=0.75)


class MagnitudeModel:
    '''
    Allows a set of measurements to be displayed on a chart as magnitude responses.
    '''

    def __init__(self, chart):
        self._chart = chart
        self._windowed = []
        self._fft = None
        self._linToLog = None

    def accept(self, windowed):
        '''
        Passes the gated, windowed data into the model.
        :param windowed: the windowed data.
        :return:
        '''
        self._windowed = windowed
        self._fft = None
        self._linToLog = None

    def display(self):
        '''
        Shows the magnitude chart
        :return:
        '''
        self._analyse()
        self._chart.getPlotItem().clear()
        for idx, x in enumerate(self._linToLog):
            self._chart.plot(x[1], 20 * np.log10(abs(x[0])), pen=(idx, len(self._linToLog)))

    def _analyse(self):
        '''
        Runs FFT and linToLog against the windowed datas.
        :return:
        '''
        if not self._fft:
            self._fft = [fft(x.samples) for x in self._windowed]
            self._linToLog = [linToLog(x[0], 48000 / x[1]) for x in self._fft]
