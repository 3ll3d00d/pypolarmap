import numpy as np

from meascalcs import *


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
            self._chart.plot(x[1], abs(x[0]), pen=(idx, len(self._linToLog)))

    def _analyse(self):
        '''
        Runs FFT and linToLog against the windowed datas.
        :return:
        '''
        if not self._fft:
            self._fft = [fft(x.samples) for x in self._windowed]
            self._linToLog = [linToLog(x[0], 48000 / x[1]) for x in self._fft]
