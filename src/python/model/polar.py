import numpy as np


class PolarModel:
    '''
    Allows a set of FRs to be displayed as a directivity sonargram.
    '''

    def __init__(self, chart):
        self._chart = chart
        self._chart.setPredefinedGradient('thermal')
        self._imgData = None

    def accept(self, logSpacedResponses):
        '''
        Passes the magnitudes responses into the model.
        :param logSpacedResponses: the output from meascalcs.linToLog.
        :return:
        '''
        self._responses = logSpacedResponses
        self._prepareImage()

    def display(self):
        '''
        Shows the polar chart.
        :return:
        '''
        if self._imgData is not None:
            self._chart.setImage(self._imgData)

    def _prepareImage(self):
        '''
        Converts the provided responses into a single 3d array suitable for display by an ImageItem.
        :return:
        '''
        if self._responses and len(self._responses) > 0:
            # log spaced freqs will be the same for every measurement so just take the 1st one
            freqs = self._responses[0][2].tolist()
            angles = [x[0]._h for x in self._responses]
            mags = [20 * np.log10(np.abs(x[1]) * 2 / np.sum(x[0].window)) for x in self._responses]
            # set x and y scale
            # TODO store the fft and linToLog data in the Measurement so we can calculate magnitude and phase once
            self._imgData = np.array(mags).transpose()
            self._chart.imageItem.scale(24000, 180)
