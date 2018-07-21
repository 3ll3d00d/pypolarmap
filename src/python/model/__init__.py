from math import log10

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