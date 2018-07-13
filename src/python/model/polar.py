import numpy as np


class PolarModel:
    '''
    Allows a set of FRs to be displayed as a directivity sonargram.
    '''

    def __init__(self, chart, measurementModel):
        self._chart = chart
        self._axes = self._chart.canvas.figure.add_subplot(111)
        self._axes.set_xscale('log')
        self._measurementModel = measurementModel
        self._imgData = None
        self._im = None
        self._cb = None
        self._refreshData = False

    def markForRefresh(self):
        '''
        Marks this model as in need of recalculation.
        '''
        self._refreshData = True

    def display(self):
        '''
        Updates the contents of the chart.
        '''
        if self._refreshData and len(self._measurementModel) > 0:
            freqs = self._measurementModel[0].logFreqs
            angles = [x._h for x in self._measurementModel]
            self._extents = [freqs[0], freqs[-1], -angles[-1], angles[0]]
            self._imgData = np.array([x.getMagnitude(ref=1) for x in self._measurementModel])
            if self._im:
                self._im.set_data(self._imgData)
                self._cb.set_array(self._imgData)
            else:
                self._im = self._axes.imshow(self._imgData, cmap=self._chart.getColourMap('tab20'), extent=self._extents)
                self._cb = self._chart.canvas.figure.colorbar(self._im)
            self._chart.canvas.draw()
            self._refreshData = False
