import logging
from threading import Timer
from time import sleep

from matplotlib import animation
from matplotlib.gridspec import GridSpec

from model.contour import ContourModel
from model.magnitude import AnimatedSingleLineMagnitudeModel
from model.polar import PolarModel

logger = logging.getLogger('multi')


class MarkerData:
    def __init__(self):
        self.freq = 0
        self.angle = 0
        self.spl = 0
        self.di = 0
        self.power = 0

    def as_table(self):
        return [
            ['Frequency', f"{round(self.freq)} Hz"],
            ['Angle', self.angle],
            ['SPL', f"{round(self.spl, 1)} dB"],
            ['DI', f"{round(self.di, 1)} dB"],
            ['Power', f"{round(self.power, 1)} dB"]
        ]


class MultiChartModel:
    '''
    A combined sonargram, magnitude response, polar response chart where the displayed magnitude and polar response
    is driven by the position of the cursor over the sonagram.
    '''

    def __init__(self, chart, measurement_model, display_model, preferences):
        self.__chart = chart
        self.__measurement_model = measurement_model
        self.name = f"multi"
        self.__data = MarkerData()
        gs = GridSpec(2, 3, width_ratios=[1, 1, 0.75])
        self.__magnitude = AnimatedSingleLineMagnitudeModel(self.__chart, self.__measurement_model, display_model,
                                                            self.__data, subplot_spec=gs.new_subplotspec((0, 0), 1, 2))
        self.__sonagram = ContourModel(self.__chart, self.__measurement_model, display_model, preferences,
                                       subplot_spec=gs.new_subplotspec((1, 0), 1, 2),
                                       redraw_on_display=False, show_crosshairs=True)
        self.__polar = PolarModel(self.__chart, self.__measurement_model, display_model, self.__data,
                                  subplotSpec=gs.new_subplotspec((1, 2), 1, 1))
        self.__table_axes = self.__chart.canvas.figure.add_subplot(gs.new_subplotspec((0, 2), 1, 1))
        self.__table = None
        self.__ani = None
        self.__stopping = False
        self.__mouse_reactor = MouseReactor(0.10, self.propagateCoords)

    def __repr__(self):
        return self.name

    def display(self):
        '''
        Displays all the charts and then draws the canvas.
        :return: always true as the multi chart always redraws (otherwise you end up with lots of glitches like old
        charts being seen behind a new chart)
        '''
        self.__magnitude.display()
        self.__polar.display()
        self.__sonagram.display()
        self.__init_table()
        self.__chart.canvas.draw_idle()
        return True

    def __init_table(self):
        ''' Initialises the table '''
        if self.__table is None:
            self.__table_axes.axis('off')
            table_data = self.__data.as_table()
            self.__table = self.__table_axes.table(cellText=table_data, loc='center', bbox=(0.1, 0.2, 0.7, 0.6))
            self.__table.auto_set_font_size(value=False)
            for idx, value in enumerate(table_data):
                key_cell = self.__table[idx, 0]
                value_cell = self.__table[idx, 1]
                key_cell._loc = 'right'
                value_cell._loc = 'left'
                key_cell.set_fontsize(12)
                value_cell.set_fontsize(12)
                if idx == 0:
                    key_cell.visible_edges = 'RB'
                    value_cell.visible_edges = 'B'
                elif idx == len(table_data) - 1:
                    key_cell.visible_edges = 'RT'
                    value_cell.visible_edges = 'T'
                else:
                    key_cell.visible_edges = 'RTB'
                    value_cell.visible_edges = 'TB'
        if self.__ani is None:
            logger.info(f"Starting animation in {self.name}")
            self.__ani = animation.FuncAnimation(self.__chart.canvas.figure, self.redraw, interval=50,
                                                 init_func=self.init_animation, blit=True, save_count=50, repeat=False)

    def init_animation(self):
        return self.__table,

    def redraw(self, frame, *fargs):
        for idx, value in enumerate(self.__data.as_table()):
            self.__table[idx, 1].get_text().set_text(' ' if self.__stopping else value[1])
        return self.__table,

    def hide(self):
        ''' Reacts to the chart no longer being visible by stopping the animation '''
        logger.info(f"Hiding {self.name}")
        self.__sonagram.clear(draw=False)
        self.__polar.clear(draw=False)
        self.__magnitude.clear(draw=False)
        self.__stopping = True
        self.stop_animation()
        sleep(0.125)
        self.__stopping = False
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

    def update_decibel_range(self, draw=True):
        '''
        Updates the decibel range on the charts.
        '''
        # we have to redraw otherwise the grid & labels don't update properly because of blitting
        self.__magnitude.clear()
        self.__magnitude.update_decibel_range(draw=False)
        self.__magnitude.__refresh_data = True
        self.__magnitude.display()
        self.__polar.update_decibel_range(draw=False)
        self.__sonagram.update_decibel_range(draw=False)
        if draw:
            self.__chart.canvas.draw_idle()

    def propagateCoords(self):
        '''
        Propagates the mouse cursor position to the magnitude & polar models.
        '''
        if self.__sonagram.cursor_x is not None and self.__sonagram.cursor_y is not None:
            if self.__magnitude.y_position != self.__sonagram.cursor_y:
                self.__magnitude.x_position = self.__sonagram.cursor_x
                self.__magnitude.y_position = self.__sonagram.cursor_y
                self.__polar.xPosition = self.__sonagram.cursor_x
                self.__polar.yPosition = self.__sonagram.cursor_y


class MouseReactor(object):
    '''
    A timer which updates the mouse position on the downstream charts periodically.
    '''

    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.daemon = True
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
