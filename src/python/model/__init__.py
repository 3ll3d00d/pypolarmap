from math import log10

import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import Formatter, NullFormatter, EngFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable

SINGLE_SUBPLOT_SPEC = GridSpec(1, 1).new_subplotspec((0, 0), 1, 1)


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
    :return: max, min, steps, fillSteps
    '''
    vmax = np.math.ceil(np.amax(data))
    vmin = vmax - maxRange
    steps = np.sort(np.concatenate((np.arange(vmax, vmax - 14, -2), np.arange(vmax - 18, vmin - 6, -6))))
    fillSteps = np.sort(np.arange(vmax, vmin, -0.05))
    return vmax, vmin, steps, fillSteps


def setYLimits(axes, dBRange):
    '''
    Updates the decibel range on the chart.
    :param axes: the axes.
    :param dBRange: the new range.
    '''
    if axes is not None:
        ylim = axes.get_ylim()
        axes.set_ylim(bottom=ylim[1] - dBRange, top=ylim[1])


def colorbar(mappable, **kwargs):
    '''
    Creates a colour bar for a given plot that will exist at a specific position relative to the given chart.
    :param mappable: the plot.
    :param **kwargs: passed through to colorbar.
    :return: the colorbar.
    '''
    ax = mappable.ax
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    return fig.colorbar(mappable, cax=cax, **kwargs)
