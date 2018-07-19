from model.contour import ContourModel
from model.magnitude import MagnitudeModel
from model.measurement import MODAL_MAGNITUDE_DATA


class ModalParameterModel:
    '''
    Parameters to feed into the modal analyser.
    '''

    def __init__(self, measurementDistance, driverRadius, modalCoeffs, f0, q0, transFreq, lfGain, boxRadius):
        self.__boxRadius = boxRadius
        self.__lfGain = lfGain
        self.__transFreq = transFreq
        self.__q0 = q0
        self.__f0 = f0
        self.__modalCoeffs = modalCoeffs
        self.__driverRadius = driverRadius
        self.__measurementDistance = measurementDistance
        self.__refreshData = False

    @property
    def measurementDistance(self):
        return self.__measurementDistance

    @measurementDistance.setter
    def measurementDistance(self, measurementDistance):
        self.__measurementDistance = measurementDistance
        self.__refreshData = True

    @property
    def driverRadius(self):
        return self.__driverRadius

    @driverRadius.setter
    def driverRadius(self, driverRadius):
        self.__driverRadius = driverRadius
        self.__refreshData = True

    @property
    def modalCoeffs(self):
        return self.__modalCoeffs

    @modalCoeffs.setter
    def modalCoeffs(self, modalCoeffs):
        self.__modalCoeffs = modalCoeffs
        self.__refreshData = True

    @property
    def f0(self):
        return self.__f0

    @f0.setter
    def f0(self, f0):
        self.__f0 = f0
        self.__refreshData = True

    @property
    def q0(self):
        return self.__q0

    @q0.setter
    def q0(self, q0):
        self.__q0 = q0
        self.__refreshData = True

    @property
    def transFreq(self):
        return self.__transFreq

    @transFreq.setter
    def transFreq(self, transFreq):
        self.__transFreq = transFreq
        self.__refreshData = True

    @property
    def lfGain(self):
        return self.__lfGain

    @lfGain.setter
    def lfGain(self, lfGain):
        self.__lfGain = lfGain
        self.__refreshData = True

    @property
    def boxRadius(self):
        return self.__boxRadius

    @boxRadius.setter
    def boxRadius(self, boxRadius):
        self.__boxRadius = boxRadius
        self.__refreshData = True

    @property
    def shouldRefresh(self):
        return self.__refreshData


class ModalModel(ContourModel):
    '''
    Displays the
    '''

    def __init__(self, chart, measurementModel, contourInterval, modalParameters):
        super().__init__(chart, measurementModel, contourInterval, type=MODAL_MAGNITUDE_DATA)
        self._modalParams = modalParameters

    def display(self):
        '''
        Updates the contents of the chart.
        '''
        if self.shouldRefresh() and len(self._measurementModel) > 0:
            self._measurementModel.generateModalResponse(self._modalParams)
            super().display()

    def shouldRefresh(self):
        return self._modalParams.shouldRefresh or super().shouldRefresh()
