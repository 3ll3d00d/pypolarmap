from math import log10

import numpy as np
from matplotlib.ticker import Formatter, NullFormatter, EngFormatter


class PrintFirstHalfFormatter(Formatter):
    '''
    A custom formatter which uses a NullFormatter for some labels and delegates to another formatter for others.
    '''

    def __init__(self, other, maxVal=5):
        self.__other = other
        self.__null = NullFormatter()
        self.__max = log10(maxVal)

    def __call__(self, x, pos=None):
        func = self.__other if self.shouldShow(x) else self.__null
        return func(x, pos)

    def shouldShow(self, x):
        return log10(x) % 1 <= self.__max


def configureFreqAxisFormatting(axes):
    '''
    Configures the x axis of the supplied axes to render Frequency values in a log format.
    :param axes:
    '''
    hzFormatter = EngFormatter(places=0)
    axes.get_xaxis().set_major_formatter(hzFormatter)
    axes.get_xaxis().set_minor_formatter(PrintFirstHalfFormatter(hzFormatter))


def formatAxes_dBFS_Hz(axes):
    '''
    Applies formatting applicable to a dbFS vs Hz line chart.
    :param axes: the axes to format.
    '''
    axes.set_xlim(left=20, right=20000)
    axes.grid(linestyle='-', which='major')
    axes.grid(linestyle='--', which='minor')
    axes.set_ylabel('dBFS')
    axes.set_xlabel('Hz')


def calculate_dBFS_Scales(data, maxRange=60):
    '''
    Calculates the min/max in the data and returns the steps to use when displaying lines on a chart, this uses -2 for
    the first 12 and then -6 thereafter.
    :param data: the data.
    :param maxRange: the max range.
    :return: max, min, steps
    '''
    vmax = np.math.ceil(np.amax(data))
    vmin = max(vmax - maxRange, np.math.floor(np.amin(data)))
    steps = np.sort(np.concatenate((np.arange(vmax - 2, vmax - 12, -2), np.arange(vmax - 18, vmin, -6))))
    return vmax, vmin, steps
