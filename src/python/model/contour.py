import numpy as np
from matplotlib.gridspec import GridSpec

from model import configureFreqAxisFormatting, calculate_dBFS_Scales
from model.measurement import CLEAR_MEASUREMENTS, ANALYSED


class ContourModel:
    '''
    Allows a set of FRs to be displayed as a directivity sonargram.
    '''

    def __init__(self, chart, measurementModel, type, subplotSpec=GridSpec(1, 1).new_subplotspec((0, 0), 1, 1),
                 cbSubplotSpec=None):
        '''
        Creates a new contour model.
        :param chart: the MplWidget that owns the canvas onto which the chart will be drawn.
        :param measurementModel: the underlying measurements.
        :param type: the type of data to present.
        :param subplotSpec: the spec for the subplot, defaults to a single plot.
        :param cbSubplotSpec: the spec for the colorbar, defaults to put it anywhere you like.
        '''
        self._chart = chart
        self._axes = None
        self._subplotSpec = subplotSpec
        self._initChart(subplotSpec)
        self._measurementModel = measurementModel
        self._selectedCmap = 'bgyw'
        self._type = type
        self._data = None
        self._tc = None
        self._tcf = None
        self._cbAxes = None
        self._cbSubplotSpec = cbSubplotSpec
        self._cid = []
        self._refreshData = False
        self._measurementModel.registerListener(self)
        self._recordY = False
        self.cursorX = None
        self.cursorY = None

    def shouldRefresh(self):
        return self._refreshData

    def _initChart(self, subplotSpec):
        '''
        Initialises the chart with the default configuration.
        :param subplotSpec: the spec for the subplot.
        '''
        self._axes = self._chart.canvas.figure.add_subplot(subplotSpec)
        self._axes.axis('auto')
        self._axes.set_xscale('log')
        self._axes.set_xlabel('Hz')
        self._axes.set_ylabel('Degrees')
        self._axes.grid(linestyle='-', which='major', linewidth=1, alpha=0.5)
        self._axes.grid(linestyle='--', which='minor', linewidth=1, alpha=0.5)

    def onUpdate(self, type, **kwargs):
        '''
        Handles events from the measurement model.
        :param type: the type.
        :param kwargs: any additional args.
        :return:
        '''
        if type == ANALYSED:
            self._refreshData = True
        elif type == CLEAR_MEASUREMENTS:
            self.clear()

    def display(self):
        '''
        Updates the contents of the chart.
        '''
        if self._refreshData and len(self._measurementModel) > 0:
            self._data = self._measurementModel.getContourData(type=self._type)
            self._extents = [np.amin(self._data['x']), np.amax(self._data['x']),
                             np.amax(self._data['y']), np.amin(self._data['y'])]
            if self._tcf:
                self.clear()
            vmax, vmin, steps = calculate_dBFS_Scales(self._data['z'])
            self._tc = self._axes.tricontour(self._data['x'], self._data['y'], self._data['z'], steps, linewidths=0.5,
                                             colors='k')
            self._tcf = self._axes.tricontourf(self._data['x'], self._data['y'], self._data['z'], steps,
                                               cmap=self._chart.getColourMap(self._selectedCmap))

            self.connectMouse()
            if self._cbSubplotSpec is not None:
                self._cbAxes = self._chart.canvas.figure.add_subplot(self._cbSubplotSpec)
                self._cb = self._chart.canvas.figure.colorbar(self._tcf, cax=self._cbAxes)
            else:
                self._cb = self._chart.canvas.figure.colorbar(self._tcf)
            configureFreqAxisFormatting(self._axes)
            self._tcf.set_clim(vmin=vmin, vmax=vmax)
            self._chart.canvas.draw()
            self._refreshData = False

    def recordDataCoords(self, event):
        '''
        Records the current location of the mouse
        :param event: the event.
        '''
        if event is not None and self._recordY:
            self.cursorX = event.xdata
            self.cursorY = event.ydata

    def enterAxes(self, event):
        '''
        Start recording the y position if the mouse is in the contour plot.
        :param event: the location event.
        '''
        self._recordY = event.inaxes is self._axes

    def leaveAxes(self, event):
        '''
        Stop recording the y position if the mouse leaves the contour plot.
        :param event: the location event.
        '''
        if event.inaxes is self._axes:
            self._recordY = False

    def connectMouse(self):
        '''
        Ensure that the y position is recorded when the mouse moves around the contour map.
        :return:
        '''
        self._cid.append(self._chart.canvas.mpl_connect('motion_notify_event', self.recordDataCoords))
        self._cid.append(self._chart.canvas.mpl_connect('axes_enter_event', self.enterAxes))
        self._cid.append(self._chart.canvas.mpl_connect('axes_leave_event', self.leaveAxes))

    def updateColourMap(self, cmap):
        '''
        Updates the currently selected colour map.
        :param cmap: the cmap name.
        '''
        cmap = self._chart.getColourMap(cmap)
        if self._tcf:
            self._tcf.set_cmap(cmap)
            self._chart.canvas.draw()
        self._selectedCmap = cmap

    def clear(self):
        '''
        clears the graph and disconnects the handlers
        '''
        if self._tcf:
            for cid in self._cid:
                self._chart.canvas.mpl_disconnect(cid)
            self._cid = []
            self._tc = None
            self._tcf = None
            self._chart.canvas.figure.clear()
            self._initChart(self._subplotSpec)
            self._chart.canvas.draw()
