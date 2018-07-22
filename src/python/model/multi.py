from threading import Timer

from matplotlib.gridspec import GridSpec

from model.contour import ContourModel
from model.magnitude import AnimatedSingleLineMagnitudeModel
from model.polar import PolarModel


class MultiChartModel:
    '''
    A combined sonargram, magnitude response, polar response chart.
    '''

    def __init__(self, chart, measurementModel, type):
        self._chart = chart
        self._measurementModel = measurementModel
        self._type = type
        # 2 rows, 4 cols to make room for the colorbar
        gs = GridSpec(2, 4, width_ratios=[1, 1, 0.05, 0.75])
        self._magnitude = AnimatedSingleLineMagnitudeModel(self._chart, self._measurementModel, type=type,
                                                           subplotSpec=gs.new_subplotspec((0, 0), 1, 4))
        self._sonagram = ContourModel(self._chart, self._measurementModel, type,
                                      subplotSpec=gs.new_subplotspec((1, 0), 1, 2),
                                      cbSubplotSpec=gs.new_subplotspec((1, 2), 1, 1))
        self._polar = PolarModel(self._chart, self._measurementModel, subplotSpec=gs.new_subplotspec((1, 3), 1, 1))
        # todo add polar chart
        self._mouseReactor = MouseReactor(0.10, self.propagateY)

    def display(self):
        self._magnitude.display()
        self._polar.display()
        # display last as this one does the canvas draw
        self._sonagram.display()

    def propagateY(self):
        '''
        Propagates the mouse cursor position to the magnitude model.
        '''
        if self._sonagram.cursorX is not None and self._sonagram.cursorY is not None:
            if self._magnitude.yPosition != self._sonagram.cursorY:
                self._magnitude.yPosition = self._sonagram.cursorY
                self._polar.xPosition = self._sonagram.cursorX


class MouseReactor(object):
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