from threading import Timer

from matplotlib.gridspec import GridSpec

from model.contour import ContourModel
from model.magnitude import AnimatedSingleLineMagnitudeModel
from model.polar import PolarModel


class MultiChartModel:
    '''
    A combined sonargram, magnitude response, polar response chart where the displayed magnitude and polar response
    is driven by the position of the cursor over the sonagram.
    '''

    def __init__(self, chart, measurementModel, type, display_model, preferences):
        self._chart = chart
        self._measurementModel = measurementModel
        self._type = type
        self.name = f"multi_{self._type}"
        gs = GridSpec(2, 3, width_ratios=[1, 1, 0.75])
        self._magnitude = AnimatedSingleLineMagnitudeModel(self._chart, self._measurementModel, display_model,
                                                           preferences, type=type,
                                                           subplotSpec=gs.new_subplotspec((0, 0), 1, 3))
        self._sonagram = ContourModel(self._chart, self._measurementModel, type, display_model,
                                      subplotSpec=gs.new_subplotspec((1, 0), 1, 2),
                                      redrawOnDisplay=False)
        self._polar = PolarModel(self._chart, self._measurementModel, display_model, type=type,
                                 subplotSpec=gs.new_subplotspec((1, 2), 1, 1))
        self._mouseReactor = MouseReactor(0.10, self.propagateCoords)

    def __repr__(self):
        return self.name

    def display(self):
        '''
        Displays all the charts and then draws the canvas.
        :return: always true as the multi chart always redraws (otherwise you end up with lots of glitches like old
        charts being seen behind a new chart)
        '''
        self._magnitude.display()
        self._polar.display()
        self._sonagram.display()
        self._chart.canvas.draw_idle()
        return True

    def hide(self):
        ''' Reacts to the chart no longer being visible by stopping the animation '''
        self._polar.stop_animation()
        self._magnitude.stop_animation()

    def updateDecibelRange(self, dBRange, draw=True):
        '''
        Updates the decibel range on the charts.
        :param dBRange: the new range.
        '''
        # we have to redraw otherwise the grid & labels don't update properly because of blitting
        self._magnitude.clear()
        self._magnitude.updateDecibelRange(dBRange, draw=False)
        self._magnitude._refreshData = True
        self._magnitude.display()

        self._polar.updateDecibelRange(dBRange, draw=False)
        self._sonagram.updateDecibelRange(dBRange, draw=False)
        if draw:
            self._chart.canvas.draw_idle()

    def propagateCoords(self):
        '''
        Propagates the mouse cursor position to the magnitude & polar models.
        '''
        if self._sonagram.cursorX is not None and self._sonagram.cursorY is not None:
            if self._magnitude.yPosition != self._sonagram.cursorY:
                self._magnitude.yPosition = self._sonagram.cursorY
                self._polar.xPosition = self._sonagram.cursorX


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
