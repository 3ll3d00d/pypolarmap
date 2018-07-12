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

    def __init__(self, chart, polar):
        self._chart = chart
        self._polarModel = polar
        self._measurements = []
        self._fft = None
        self._linToLog = None

    def accept(self, measurements):
        '''
        Passes the gated, windowed data into the model.
        :param measurements: the windowed data.
        :return:
        '''
        self._measurements = measurements
        self._fft = None
        self._linToLog = None

    def display(self):
        '''
        Shows the magnitude chart
        :return:
        '''
        self._analyse()
        self._chart.getPlotItem().clear()
        # todo consider making this user selectable, e.g. to allow for dB SPL output
        ref = 1
        for idx, x in enumerate(self._linToLog):
            # Scale the magnitude of FFT by indow and factor of 2 because we are using half of FFT spectrum.
            mag = np.abs(x[1]) * 2 / np.sum(x[0].window)
            self._chart.plot(x[2], 20 * np.log10(mag/ref), pen=(idx, len(self._linToLog)))
        self._polarModel.accept(self._linToLog)

    def _analyse(self):
        '''
        Runs FFT and linToLog against the windowed datas.
        This stores 2 separate 3 element tuples
         * _fft: (measurement, fft'ed data, no of points in the fft)
         * _linToLog: (measurement, log spaced fft'ed data, log spaced frequencies)
        :return:
        '''
        if not self._fft:
            self._fft = [((x,) + fft(x.samples)) for x in self._measurements]
            # TODO get
            self._linToLog = [(x[0],) + linToLog(x[1], x[0]._fs / x[2]) for x in self._fft]
