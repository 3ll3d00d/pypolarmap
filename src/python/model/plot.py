import numpy as np
from pyqtgraph import SignalProxy


class PlotModel:

    def __init__(self, chart, leftWindowSample, rightWindowSample):
        self._chart = chart
        self._leftWindowSample = leftWindowSample
        self._rightWindowSample = rightWindowSample
        self._measurements = []
        self._maxSample = 0
        self._leftLine = None
        self._rightLine = None

    def accept(self, measurements):
        self._measurements = measurements
        if len(measurements) > 0:
            self._maxSample = max([x.size() for x in measurements])
        else:
            self._maxSample = 0
        self._leftWindowSample.setMaximum(self._maxSample)
        self._leftWindowSample.setValue(0)
        self._rightWindowSample.setMaximum(self._maxSample)
        self._rightWindowSample.setValue(self._maxSample)

    def displayImpulses(self):
        # todo ensure min < max
        x = np.arange(self._maxSample)
        for idx, measurement in enumerate(self._measurements):
            self._chart.plot(x, measurement.samples, pen=(idx, len(self._measurements)))
        self.updateLeftWindow()
        self.updateRightWindow()

    def updateLeftWindow(self):
        value = self._leftWindowSample.value()
        if self._leftLine:
            self._leftLine.setValue(value)
        else:
            self._leftLine = self._chart.addLine(x=value, movable=True, name='LeftWin')
            self._leftLine.sigPositionChangeFinished.connect(self._propagateLeftWindow)
        if value > self._rightWindowSample.value():
            self._rightWindowSample.setValue(value + 1)
            self.updateRightWindow()

    def _propagateLeftWindow(self):
        self._leftWindowSample.setValue(round(self._leftLine.value()))
        self.updateLeftWindow()

    def updateRightWindow(self):
        value = self._rightWindowSample.value()
        if self._rightLine:
            self._rightLine.setValue(value)
        else:
            self._rightLine = self._chart.addLine(x=value, movable=True, name='RightWin')
            self._rightLine.sigPositionChangeFinished.connect(self._propagateRightWindow)
        if value <= self._leftWindowSample.value():
            self._leftWindowSample.setValue(value - 1)
            self.updateLeftWindow()

    def _propagateRightWindow(self):
        self._rightWindowSample.setValue(round(self._rightLine.value()))
        self.updateRightWindow()

