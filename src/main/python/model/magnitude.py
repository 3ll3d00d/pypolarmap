import logging

import numpy as np
from matplotlib import animation
from qtpy import QtCore
from qtpy.QtWidgets import QListWidgetItem

from model import configureFreqAxisFormatting, format_axes_dbfs_hz, set_y_limits, SINGLE_SUBPLOT_SPEC, \
    calculate_dBFS_Scales
from model.measurement import CLEAR_MEASUREMENTS, LOAD_MEASUREMENTS

logger = logging.getLogger('magnitude')


class MagnitudeModel:
    '''
    Allows a set of measurements to be displayed on a chart as magnitude responses.
    '''

    def __init__(self, chart, measurement_model, display_model, model_listener=None,
                 subplot_spec=SINGLE_SUBPLOT_SPEC, show_legend=True, selector=None, depends_on=lambda: False):
        self.__chart = chart
        self.__axes = self.__chart.canvas.figure.add_subplot(subplot_spec)
        format_axes_dbfs_hz(self.__axes)
        self.__curves = {}
        self.__refresh_data = False
        self.name = f"magnitude"
        self.__measurement_model = measurement_model
        self.__model_listener = model_listener
        self.__show_legend = show_legend
        self.__measurement_model.register_listener(self)
        self.__display_model = display_model
        self.__selector = selector
        self.__depends_on = depends_on
        if self.__selector is not None:
            self.__selector.itemSelectionChanged.connect(self.set_visible)
        self.update_decibel_range(draw=False)

    def set_visible(self):
        ''' ensures the visible curves tracks the contents of the selector '''
        selected = [x.text() for x in self.__selector.selectedItems()]
        for name, curve in self.__curves.items():
            curve.set_visible(name in selected)
        self.__chart.canvas.draw_idle()

    def __repr__(self):
        return self.name

    def should_refresh(self):
        return self.__refresh_data or self.__depends_on()

    def update_decibel_range(self, draw=True):
        '''
        Updates the decibel range on the chart.
        '''
        if draw:
            set_y_limits(self.__axes, self.__display_model.db_range)
            self.__chart.canvas.draw_idle()

    def display(self):
        '''
        Updates the contents of the magnitude chart
        '''
        # TODO might need to update the ylim even if we haven't refreshed
        if self.should_refresh():
            # pressure
            data = self.__measurement_model.get_magnitude_data()
            current_names = [x.display_name for x in data]
            all_y = [x.y for x in data]
            for idx, x in enumerate(data):
                self._create_or_update_curve(x, self.__axes, self.__chart.get_colour(idx, len(self.__measurement_model)))
            # power
            power = self.__measurement_model.power_response
            if power is not None:
                self._create_or_update_curve(power, self.__axes, 'k')
                all_y.append(power.y)
                current_names.append(power.display_name)
            # di
            di = self.__measurement_model.di
            if di is not None:
                self._create_or_update_curve(di, self.__axes, 'k')
                all_y.append(di.y)
                current_names.append(di.display_name)
            # scales
            self._update_y_lim(np.concatenate(all_y), self.__axes)
            # delete redundant data
            to_delete = [k for k in self.__curves.keys() if k not in current_names]
            for d in to_delete:
                self.__curves[d].remove()
                del self.__curves[d]
                for item in self.__selector.findItems(d, QtCore.Qt.MatchExactly):
                    self.__selector.takeItem(self.__selector.row(item))
            # legend
            if self.__show_legend:
                lines = self.__curves.values()
                if self.__axes.get_legend() is not None:
                    self.__axes.get_legend().remove()
                self.__axes.legend(lines, [l.get_label() for l in lines], loc=8, ncol=4, fancybox=True, shadow=True)
            # selector
            if self.__selector is not None:
                self.__selector.selectAll()
            else:
                self.__chart.canvas.draw_idle()
            self.__refresh_data = False
        else:
            ylim = self.__axes.get_ylim()
            if ylim[1] - ylim[0] != self.__display_model.db_range:
                self.update_decibel_range()

    def _update_y_lim(self, data, axes):
        configureFreqAxisFormatting(axes)
        ymax, ymin, _, _ = calculate_dBFS_Scales(data, max_range=self.__display_model.db_range)
        axes.set_ylim(bottom=ymin, top=ymax)

    def _create_or_update_curve(self, data, axes, colour):
        curve = self.__curves.get(data.display_name, None)
        if curve:
            curve.set_data(data.x, data.y)
        else:
            self.__curves[data.display_name] = axes.semilogx(data.x, data.y,
                                                     linewidth=2,
                                                     antialiased=True,
                                                     linestyle='solid',
                                                     color=colour,
                                                     label=data.display_name)[0]
            if self.__selector is not None:
                self.__selector.addItem(QListWidgetItem(data.display_name, self.__selector))

    def on_update(self, event_type, **kwargs):
        '''
        handles measurement model changes
        If event type is activation toggle then changes the associated curve visibility.
        If event type is analysis change then the model is marked for refresh.
        :param event_type: the event.
        :param idx: the measurement idx.
        '''
        if self.__model_listener:
            self.__model_listener.on_update(event_type, kwargs)
        if event_type == LOAD_MEASUREMENTS:
            self.__refresh_data = True
        elif event_type == CLEAR_MEASUREMENTS:
            self.clear()

    def clear(self):
        '''
        clears the graph.
        '''
        self.__axes.clear()
        self.__curves = {}
        format_axes_dbfs_hz(self.__axes)
        if self.__selector is not None:
            self.__selector.clear()


class AnimatedSingleLineMagnitudeModel:
    '''
    Allows a single measurement from a selection of magnitude data to be displayed on a chart.
    '''

    def __init__(self, chart, measurement_model, display_model, marker_data,
                 subplot_spec=SINGLE_SUBPLOT_SPEC, redraw_on_display=True):
        self._chart = chart
        self.__measurement_model = measurement_model
        self.__measurement_model.register_listener(self)
        self.__axes = self._chart.canvas.figure.add_subplot(subplot_spec)
        self.__secondary_axes = self.__axes.twinx()
        self.__secondary_axes.set_ylim(bottom=0, top=30)
        format_axes_dbfs_hz(self.__axes)
        self.name = f"single-magnitude"
        self.__refresh_data = False
        self.x_position = None
        self.y_position = None
        self.__pressure_data = None
        self.__pressure_curve = None
        self.__pressure_marker = None
        self.__power_data = None
        self.__power_curve = None
        self.__power_marker = None
        self.__di_data = None
        self.__di_curve = None
        self.__di_marker = None
        self.__vline = None
        self.__ani = None
        self.__y_range_update_required = False
        self.__redraw_on_display = redraw_on_display
        self.__display_model = display_model
        self.__marker_data = marker_data

    def __repr__(self):
        return self.name

    def should_refresh(self):
        return self.__refresh_data

    def update_decibel_range(self, draw=True):
        '''
        Updates the decibel range on the chart.
        '''
        self.__y_range_update_required = True
        set_y_limits(self.__axes, self.__display_model.db_range)
        if self.__ani:
            # have to clear the blit cache to get the r grid to redraw as per
            # https://stackoverflow.com/questions/25021311/matplotlib-animation-updating-radial-view-limit-for-polar-plot
            self.__ani._blit_cache.clear()
        if draw:
            self._chart.canvas.draw_idle()
            self.__y_range_update_required = False

    def display(self):
        '''
        Gets fresh data and redraws.
        :return: true if it redrew.
        '''
        redrew = False
        if self.should_refresh():
            if self.__pressure_curve is None:
                # pressure
                self.__pressure_data = self.__measurement_model.get_magnitude_data()
                self.__pressure_curve = self.__axes.semilogx(self.__pressure_data[0].x,
                                                             [np.nan] * len(self.__pressure_data[0].x),
                                                             linewidth=2,
                                                             antialiased=True,
                                                             linestyle='solid')[0]
                self.__pressure_marker = self.__axes.plot(0, 0, 'bo', markersize=8)[0]
                all_data = [x.y for x in self.__pressure_data]
                # directivity
                if self.__di_data:
                    self.__di_curve = self.__secondary_axes.semilogx(self.__di_data[0].x,
                                                                    [np.nan] * len(self.__pressure_data[0].x),
                                                                    linewidth=2,
                                                                    antialiased=True,
                                                                    linestyle='--')[0]
                    self.__di_marker = self.__secondary_axes.plot(0, 0, 'bo', markersize=8)[0]
                if self.__power_data:
                    # power
                    self.__power_curve = self.__axes.semilogx(self.__power_data.x,
                                                              self.__power_data.y,
                                                              linewidth=2,
                                                              antialiased=True,
                                                              color='k',
                                                              linestyle='solid')[0]
                    self.__power_marker = self.__axes.plot(0, 0, 'ko', markersize=8)[0]
                    all_data.append(self.__power_data.y)
                # line
                self.__vline = self.__axes.axvline(x=0, linewidth=2, color='gray', linestyle=':')
                # scales
                ymax, ymin, _, _ = calculate_dBFS_Scales(np.concatenate(all_data),
                                                         max_range=self.__display_model.db_range)
                self.__axes.set_ylim(bottom=ymin, top=ymax, auto=False)
                configureFreqAxisFormatting(self.__axes)
                self.__y_range_update_required = False
                self.__refresh_data = False
                redrew = True
        else:
            if self.__pressure_curve is not None:
                if self.__y_range_update_required:
                    self.update_decibel_range(self.__redraw_on_display)
        # make sure we are animating
        if self.__ani is None and self.__pressure_data is not None:
            logger.info(f"Starting animation in {self.name}")
            self.__ani = animation.FuncAnimation(self._chart.canvas.figure, self.redraw, interval=50,
                                                 init_func=self.initAnimation, blit=True, save_count=50, repeat=False)
        return redrew

    def initAnimation(self):
        '''
        Inits a blank screen.
        :return: the curve artist.
        '''
        self.__pressure_curve.set_ydata([np.nan] * len(self.__pressure_data[0].x))
        vals = [self.__pressure_curve, self.__pressure_marker]
        if self.__power_data:
            vals.append(self.__power_curve)
            vals.append(self.__power_marker)
        if self.__di_data:
            vals.append(self.__di_curve)
            vals.append(self.__di_data)
        vals.append(self.__vline)
        return vals

    def __find_nearest_xy(self, curve):
        return np.argmax(curve.x >= self.x_position)

    def redraw(self, frame, *fargs):
        '''
        Redraws the graph based on the yPosition.
        '''
        curve_data, curve_idx = self.find_nearest_xy_data()
        if curve_idx != -1:
            colour = self._chart.get_colour(curve_idx, len(self.__measurement_model))
            self.__pressure_curve.set_ydata(curve_data.y)
            self.__pressure_curve.set_color(colour)
            idx = self.__find_nearest_xy(curve_data)
            self.__pressure_marker.set_data(curve_data.x[idx], curve_data.y[idx])
            self.__marker_data.freq = curve_data.x[idx]
            self.__marker_data.spl = curve_data.y[idx]
            self.__pressure_marker.set_color(colour)
            self.__vline.set_xdata([curve_data.x[idx], curve_data.x[idx]])
            if self.__power_data:
                di_y = (curve_data.y * curve_data.y) / self.__power_data.y
                di_y += (0.0 - di_y[0])
                self.__di_curve.set_ydata(di_y)
                self.__di_curve.set_color(colour)
                self.__di_marker.set_color(colour)
                self.__di_marker.set_data(curve_data.x[idx], di_y[idx])
                self.__power_marker.set_data(curve_data.x[idx], self.__power_data.y[idx])
                self.__marker_data.di = di_y[idx]
                self.__marker_data.power = self.__power_data.y[idx]
        if self.__power_data:
            return self.__pressure_curve, self.__pressure_marker, self.__power_curve, self.__power_marker, self.__di_curve, self.__di_marker, self.__vline
        else:
            return self.__pressure_curve, self.__pressure_marker, self.__vline

    def find_nearest_xy_data(self):
        '''
        Searches the available data to find the curve that is the closest hAngle to our current yPosition.
        :return: (curve_idx, curve_data) or (-1, None) if nothing is found.
        '''
        curve_idx = -1
        curve_data = None
        delta = 100000000
        if self.y_position is not None:
            for idx, x in enumerate(self.__pressure_data):
                new_delta = abs(self.y_position - x.h)
                if new_delta < delta:
                    delta = new_delta
                    curve_idx = idx
                    curve_data = x
                elif new_delta > delta:
                    break
        return curve_data, curve_idx

    def on_update(self, type, **kwargs):
        '''
        handles measurement model changes
        If event type is activation toggle then changes the associated curve visibility.
        If event type is analysis change then the model is marked for refresh.
        :param idx: the measurement idx.
        '''
        if type == LOAD_MEASUREMENTS:
            self.__refresh_data = True
        elif type == CLEAR_MEASUREMENTS:
            self.clear()

    def clear(self, draw=True):
        '''
        clears the graph.
        '''
        self.stop_animation()
        self.__axes.clear()
        self.__pressure_curve = None
        format_axes_dbfs_hz(self.__axes)
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
            self.__refresh_data = True
            ani._stop()
