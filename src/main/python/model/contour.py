import logging

import numpy as np
from matplotlib import animation

from model import configureFreqAxisFormatting, calculate_dBFS_Scales, colorbar, SINGLE_SUBPLOT_SPEC
from model.measurement import CLEAR_MEASUREMENTS, LOAD_MEASUREMENTS
from model.preferences import DISPLAY_COLOUR_MAP

logger = logging.getLogger('contour')


class ContourModel:
    '''
    Allows a set of FRs to be displayed as a directivity sonargram.
    '''

    def __init__(self, chart, measurement_model, display_model, preferences,
                 subplot_spec=SINGLE_SUBPLOT_SPEC, redraw_on_display=True, depends_on=lambda: False,
                 show_crosshairs=False):
        '''
        Creates a new contour model.
        :param chart: the MplWidget that owns the canvas onto which the chart will be drawn.
        :param measurement_model: the underlying measurements.
        :param subplot_spec: the spec for the subplot, defaults to a single plot.
        :param cbSubplotSpec: the spec for the colorbar, defaults to put it anywhere you like.
        '''
        self.__chart = chart
        self.__axes = None
        self.__crosshair_axes = None
        self.__show_crosshairs = show_crosshairs
        self.__subplot_spec = subplot_spec
        self.__init_chart(subplot_spec)
        self.__measurement_model = measurement_model
        self.__depends_on = depends_on
        self.__selected_cmap = preferences.get(DISPLAY_COLOUR_MAP)
        self.__cmap_changed = False
        self.name = 'contour'
        self.__data = None
        self.__tc = None
        self.__tcf = None
        self.__cid = []
        self.__refresh_data = False
        self.__measurement_model.register_listener(self)
        self.__record_y = False
        self.__dragging = False
        self.cursor_x = None
        self.cursor_y = None
        self.__crosshair_h = None
        self.__crosshair_v = None
        self.__ani = None
        self.__redraw_on_display = redraw_on_display
        self.__display_model = display_model
        self.__required_clim = None
        self.__extents = []

    def __repr__(self):
        return self.name

    def should_refresh(self):
        return self.__refresh_data or self.__depends_on

    def __init_chart(self, subplotSpec):
        '''
        Initialises the chart with the default configuration.
        :param subplotSpec: the spec for the subplot.
        '''
        if self.__axes is None:
            self.__axes = self.__chart.canvas.figure.add_subplot(subplotSpec)
        if self.__show_crosshairs is True and self.__crosshair_axes is None:
            self.__crosshair_axes = self.__axes.twinx()
            self.__crosshair_axes.get_yaxis().set_visible(False)
        self.__axes.axis('auto')
        self.__axes.set_xscale('log')
        self.__axes.set_xlabel('Hz')
        self.__axes.set_ylabel('Degrees')
        self.__axes.grid(linestyle='-', which='major', linewidth=1, alpha=0.5)
        self.__axes.grid(linestyle='--', which='minor', linewidth=1, alpha=0.5)

    def update_decibel_range(self, draw=True):
        '''
        Updates the decibel range on the chart.
        '''
        # record the target clim in case we don't want to draw right now
        if self.__tcf is not None:
            _, cmax = self.__tcf.get_clim()
            self.__required_clim = (cmax - self.__display_model.db_range, cmax)
            self.__tcf.set_clim(vmin=self.__required_clim[0], vmax=self.__required_clim[1])
        if draw:
            self.__required_clim = None
            self.__chart.canvas.draw_idle()

    def on_update(self, type, **kwargs):
        '''
        Handles events from the measurement model.
        :param type: the type.
        :param kwargs: any additional args.
        :return:
        '''
        if type == LOAD_MEASUREMENTS:
            self.__refresh_data = True
        elif type == CLEAR_MEASUREMENTS:
            self.clear()

    def display(self):
        '''
        Updates the contents of the chart. This occurs if we need to recalculate the plot data (i.e. if the underlying
        data has changed) or if we are redisplaying this chart and the y range has changed since it was last visible.
        :return: true if it redrew.
        '''
        if len(self.__measurement_model) > 0:
            if self.__refresh_data:
                self.__data = self.__measurement_model.get_contour_data()
                self.__extents = [np.nanmin(self.__data['x']), np.nanmax(self.__data['x']),
                                  np.nanmax(self.__data['y']), np.nanmin(self.__data['y'])]
                if self.__tcf:
                    self.clear(disconnect=False)
                self.__redraw()
                self.connect_mouse()
                if self.__redraw_on_display:
                    self.__chart.canvas.draw_idle()
                self.__refresh_data = False
                return True
            else:
                # this is called when the owning tab is selected so we need to update the clim if the y range
                # was changed while this chart was off screen
                if self.__tcf is not None and self.__required_clim is not None:
                    self.update_decibel_range(draw=self.__redraw_on_display)
                    return self.__redraw_on_display
                if self.__cmap_changed:
                    self.__chart.canvas.draw_idle()
                    self.__cmap_changed = False
        return False

    def __redraw(self):
        '''
        draws the contours and the colorbar.
        :return:
        '''
        vmax, vmin, steps, fill_steps = calculate_dBFS_Scales(self.__data['z'],
                                                              max_range=self.__display_model.db_range,
                                                              vmax_to_round=False)
        actual_vmax = np.math.ceil(np.nanmax(self.__data['z']))
        line_offset = actual_vmax - vmax
        line_steps = steps + line_offset
        self.__tc = self.__axes.tricontour(self.__data['x'], self.__data['y'], self.__data['z'],
                                           line_steps if not self.__display_model.normalised else line_steps - np.max(line_steps) - 2,
                                           linewidths=0.5, colors='k', linestyles='--')
        self.__tc = self.__axes.tricontour(self.__data['x'], self.__data['y'], self.__data['z'],
                                           levels=[actual_vmax - 6] if not self.__display_model.normalised else [-6],
                                           linewidths=1.5, colors='k')
        self.__tcf = self.__axes.tricontourf(self.__data['x'], self.__data['y'], self.__data['z'], fill_steps,
                                             vmin=vmin, vmax=vmax,
                                             cmap=self.__chart.get_colour_map(self.__selected_cmap))
        self._cb = colorbar(self.__tcf)
        self._cb.set_ticks(steps)
        configureFreqAxisFormatting(self.__axes)
        self.__tcf.set_clim(vmin=vmin, vmax=vmax)
        if self.__crosshair_axes is not None:
            xlim = self.__axes.get_xlim()
            ylim = self.__axes.get_ylim()
            self.__crosshair_axes.set_xlim(left=xlim[0], right=xlim[1])
            self.__crosshair_axes.set_ylim(bottom=ylim[0], top=ylim[1])
            self.__crosshair_h = self.__crosshair_axes.axhline(color='k', linestyle=':')
            self.__crosshair_v = self.__crosshair_axes.axvline(color='k', linestyle=':')
            if self.__ani is None:
                logger.info(f"Starting animation in {self.name}")
                self.__ani = animation.FuncAnimation(self.__chart.canvas.figure, self.__redraw_crosshairs, interval=50,
                                                     init_func=self.__init_crosshairs, blit=True, save_count=50, repeat=False)

    def __init_crosshairs(self):
        self.__crosshair_h.set_ydata([self.__extents[3], self.__extents[3]])
        self.__crosshair_v.set_xdata([self.__extents[0], self.__extents[0]])
        return self.__crosshair_h, self.__crosshair_v

    def __redraw_crosshairs(self, frame, *fargs):
        if self.cursor_y is not None:
            self.__crosshair_h.set_ydata([self.cursor_y] * 2)
        if self.cursor_x is not None:
            self.__crosshair_v.set_xdata([self.cursor_x] * 2)
        return self.__crosshair_h, self.__crosshair_v

    def recordDataCoords(self, event):
        '''
        Records the current location of the mouse
        :param event: the event.
        '''
        if event is not None and self.__record_y and self.__dragging:
            self.cursor_x = event.xdata
            self.cursor_y = event.ydata

    def enterAxes(self, event):
        '''
        Start recording the y position if the mouse is in the contour plot.
        :param event: the location event.
        '''
        self.__record_y = event.inaxes is self.__axes or self.__crosshair_axes

    def leaveAxes(self, event):
        '''
        Stop recording the y position if the mouse leaves the contour plot.
        :param event: the location event.
        '''
        if event.inaxes is self.__axes:
            self.__record_y = False

    def connect_mouse(self):
        '''
        Ensure that the y position is recorded when the mouse moves around the contour map.
        :return:
        '''
        if self.__cid is None or len(self.__cid) == 0:
            self.__cid.append(self.__chart.canvas.mpl_connect('motion_notify_event', self.recordDataCoords))
            self.__cid.append(self.__chart.canvas.mpl_connect('button_press_event', self.depress))
            self.__cid.append(self.__chart.canvas.mpl_connect('button_release_event', self.release))
            self.__cid.append(self.__chart.canvas.mpl_connect('axes_enter_event', self.enterAxes))
            self.__cid.append(self.__chart.canvas.mpl_connect('axes_leave_event', self.leaveAxes))

    def depress(self, event):
        if not event.dblclick:
            self.__dragging = True

    def release(self, event):
        self.__dragging = False

    def update_colour_map(self, cmap_name, draw=True):
        '''
        Updates the currently selected colour map.
        :param cmap_name: the cmap name.
        '''
        if cmap_name != self.__selected_cmap:
            self.__selected_cmap = cmap_name
            if self.__tcf:
                cmap = self.__chart.get_colour_map(cmap_name)
                self.__tcf.set_cmap(cmap)
                if draw:
                    self.__chart.canvas.draw_idle()
                else:
                    self.__cmap_changed = True

    def clear(self, disconnect=True, draw=True):
        '''
        clears the graph and disconnects the handlers
        '''
        if self.__tcf:
            if disconnect:
                for cid in self.__cid:
                    self.__chart.canvas.mpl_disconnect(cid)
                self.__cid = []
            self.stop_animation()
            self._cb.remove()
            self.__axes.clear()
            if self.__crosshair_axes is not None:
                self.__crosshair_axes.clear()
            self.__tc = None
            self.__tcf = None
            self.__init_chart(self.__subplot_spec)
            self.__refresh_data = True
            if draw:
                self.__chart.canvas.draw_idle()

    def stop_animation(self):
        '''
        Stops the animation.
        '''
        if self.__ani is not None:
            logger.info(f"Stopping animation in {self.name}")
            ani = self.__ani
            self.__ani = None
            ani._stop()
