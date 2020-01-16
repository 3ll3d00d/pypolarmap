import logging

import numpy as np
from matplotlib import animation

from model import configureFreqAxisFormatting, calculate_dBFS_Scales, colorbar, SINGLE_SUBPLOT_SPEC
from model.measurement import CLEAR_MEASUREMENTS, LOAD_MEASUREMENTS

logger = logging.getLogger('contour')


class ContourModel:
    '''
    Allows a set of FRs to be displayed as a directivity sonargram.
    '''

    def __init__(self, chart, measurementModel, type, display_model, subplotSpec=SINGLE_SUBPLOT_SPEC,
                 redrawOnDisplay=True, depends_on=lambda: False, show_crosshairs=False):
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
        self.__crosshair_axes = None
        self.__show_crosshairs = show_crosshairs
        self._subplotSpec = subplotSpec
        self._initChart(subplotSpec)
        self._measurementModel = measurementModel
        self.__depends_on = depends_on
        self._selectedCmap = 'bgyw'
        self._type = type
        self.name = f"contour_{self._type}"
        self._data = None
        self._tc = None
        self._tcf = None
        self._cid = []
        self._refreshData = False
        self._measurementModel.registerListener(self)
        self._recordY = False
        self.__dragging = False
        self.cursorX = None
        self.cursorY = None
        self.__crosshair_h = None
        self.__crosshair_v = None
        self.__ani = None
        self._redrawOnDisplay = redrawOnDisplay
        self.__display_model = display_model
        self._required_clim = None
        self.__extents = []

    def __repr__(self):
        return self.name

    def shouldRefresh(self):
        return self._refreshData or self.__depends_on

    def _initChart(self, subplotSpec):
        '''
        Initialises the chart with the default configuration.
        :param subplotSpec: the spec for the subplot.
        '''
        if self._axes is None:
            self._axes = self._chart.canvas.figure.add_subplot(subplotSpec)
        if self.__show_crosshairs is True and self.__crosshair_axes is None:
            self.__crosshair_axes = self._axes.twinx()
            self.__crosshair_axes.get_yaxis().set_visible(False)
        self._axes.axis('auto')
        self._axes.set_xscale('log')
        self._axes.set_xlabel('Hz')
        self._axes.set_ylabel('Degrees')
        self._axes.grid(linestyle='-', which='major', linewidth=1, alpha=0.5)
        self._axes.grid(linestyle='--', which='minor', linewidth=1, alpha=0.5)

    def updateDecibelRange(self, draw=True):
        '''
        Updates the decibel range on the chart.
        '''
        # record the target clim in case we don't want to draw right now
        if self._tcf is not None:
            _, cmax = self._tcf.get_clim()
            self._required_clim = (cmax - self.__display_model.dBRange, cmax)
            self._tcf.set_clim(vmin=self._required_clim[0], vmax=self._required_clim[1])
        if draw:
            self._required_clim = None
            self._chart.canvas.draw_idle()

    def onUpdate(self, type, **kwargs):
        '''
        Handles events from the measurement model.
        :param type: the type.
        :param kwargs: any additional args.
        :return:
        '''
        if type == LOAD_MEASUREMENTS:
            self._refreshData = True
        elif type == CLEAR_MEASUREMENTS:
            self.clear()

    def display(self):
        '''
        Updates the contents of the chart. This occurs if we need to recalculate the plot data (i.e. if the underlying
        data has changed) or if we are redisplaying this chart and the y range has changed since it was last visible.
        :return: true if it redrew.
        '''
        if len(self._measurementModel) > 0:
            if self._refreshData:
                self._data = self._measurementModel.getContourData(type=self._type)
                self.__extents = [np.nanmin(self._data['x']), np.nanmax(self._data['x']),
                                  np.nanmax(self._data['y']), np.nanmin(self._data['y'])]
                if self._tcf:
                    self.clear(disconnect=False)
                self._redraw()
                self.connectMouse()
                if self._redrawOnDisplay:
                    self._chart.canvas.draw_idle()
                self._refreshData = False
                return True
            else:
                # this is called when the owning tab is selected so we need to update the clim if the y range
                # was changed while this chart was off screen
                if self._tcf is not None and self._required_clim is not None:
                    self.updateDecibelRange(draw=self._redrawOnDisplay)
                    return self._redrawOnDisplay
        return False

    def _redraw(self):
        '''
        draws the contours and the colorbar.
        :return:
        '''
        vmax, vmin, steps, fillSteps = calculate_dBFS_Scales(self._data['z'], maxRange=self.__display_model.dBRange)
        self._tc = self._axes.tricontour(self._data['x'], self._data['y'], self._data['z'], steps, linewidths=0.5,
                                         colors='k', linestyles='--')
        self._tc = self._axes.tricontour(self._data['x'], self._data['y'], self._data['z'], levels=[vmax - 6],
                                         linewidths=1.5,
                                         colors='k')
        self._tcf = self._axes.tricontourf(self._data['x'], self._data['y'], self._data['z'], fillSteps,
                                           vmin=vmin, vmax=vmax, cmap=self._chart.getColourMap(self._selectedCmap))
        self._cb = colorbar(self._tcf)
        self._cb.set_ticks(steps)
        configureFreqAxisFormatting(self._axes)
        self._tcf.set_clim(vmin=vmin, vmax=vmax)
        if self.__crosshair_axes is not None:
            xlim = self._axes.get_xlim()
            ylim = self._axes.get_ylim()
            self.__crosshair_axes.set_xlim(left=xlim[0], right=xlim[1])
            self.__crosshair_axes.set_ylim(bottom=ylim[0], top=ylim[1])
            self.__crosshair_h = self.__crosshair_axes.axhline(color='k', linestyle=':')
            self.__crosshair_v = self.__crosshair_axes.axvline(color='k', linestyle=':')
            if self.__ani is None:
                logger.info(f"Starting animation in {self.name}")
                self.__ani = animation.FuncAnimation(self._chart.canvas.figure, self.__redraw_crosshairs, interval=50,
                                                     init_func=self.__init_crosshairs, blit=True, save_count=50, repeat=False)

    def __init_crosshairs(self):
        self.__crosshair_h.set_ydata([self.__extents[3], self.__extents[3]])
        self.__crosshair_v.set_xdata([self.__extents[0], self.__extents[0]])
        return self.__crosshair_h, self.__crosshair_v

    def __redraw_crosshairs(self, frame, *fargs):
        if self.cursorY is not None:
            self.__crosshair_h.set_ydata([self.cursorY] * 2)
        if self.cursorX is not None:
            self.__crosshair_v.set_xdata([self.cursorX] * 2)
        return self.__crosshair_h, self.__crosshair_v

    def recordDataCoords(self, event):
        '''
        Records the current location of the mouse
        :param event: the event.
        '''
        if event is not None and self._recordY and self.__dragging:
            self.cursorX = event.xdata
            self.cursorY = event.ydata

    def enterAxes(self, event):
        '''
        Start recording the y position if the mouse is in the contour plot.
        :param event: the location event.
        '''
        self._recordY = event.inaxes is self._axes or self.__crosshair_axes

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
        if self._cid is None or len(self._cid) == 0:
            self._cid.append(self._chart.canvas.mpl_connect('motion_notify_event', self.recordDataCoords))
            self._cid.append(self._chart.canvas.mpl_connect('button_press_event', self.depress))
            self._cid.append(self._chart.canvas.mpl_connect('button_release_event', self.release))
            self._cid.append(self._chart.canvas.mpl_connect('axes_enter_event', self.enterAxes))
            self._cid.append(self._chart.canvas.mpl_connect('axes_leave_event', self.leaveAxes))

    def depress(self, event):
        if not event.dblclick:
            self.__dragging = True

    def release(self, event):
        self.__dragging = False

    def updateColourMap(self, cmap, draw=True):
        '''
        Updates the currently selected colour map.
        :param cmap: the cmap name.
        '''
        cmap = self._chart.getColourMap(cmap)
        if self._tcf:
            self._tcf.set_cmap(cmap)
            if draw:
                self._chart.canvas.draw_idle()
        self._selectedCmap = cmap

    def clear(self, disconnect=True, draw=True):
        '''
        clears the graph and disconnects the handlers
        '''
        if self._tcf:
            if disconnect:
                for cid in self._cid:
                    self._chart.canvas.mpl_disconnect(cid)
                self._cid = []
            self.stop_animation()
            self._cb.remove()
            self._axes.clear()
            if self.__crosshair_axes is not None:
                self.__crosshair_axes.clear()
            self._tc = None
            self._tcf = None
            self._initChart(self._subplotSpec)
            self._refreshData = True
            if draw:
                self._chart.canvas.draw_idle()

    def stop_animation(self):
        '''
        Stops the animation.
        '''
        if self.__ani is not None:
            logger.info(f"Stopping animation in {self.name}")
            ani = self.__ani
            self.__ani = None
            ani._stop()
