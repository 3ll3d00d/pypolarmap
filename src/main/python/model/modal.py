import logging

from qtpy.QtWidgets import QDialog, QDialogButtonBox

from model.preferences import MODAL_BOX_RADIUS, MODAL_LF_GAIN, MODAL_TRANS_FREQ, MODAL_Q0, MODAL_F0, MODAL_COEFFS, \
    MODAL_DRIVER_RADIUS, MODAL_MEASUREMENT_DISTANCE, MODAL_GROUP
from ui.modalparameters import Ui_modalParametersDialog

logger = logging.getLogger('modal')


class ModalParameterModel:
    '''
    Parameters to feed into the modal analyser.
    '''

    def __init__(self, preferences):
        self.__preferences = preferences
        self.__init()
        self.__refreshData = False

    def __init(self):
        self.__boxRadius = self.__preferences.get(MODAL_BOX_RADIUS)
        self.__lfGain = self.__preferences.get(MODAL_LF_GAIN)
        self.__transFreq = self.__preferences.get(MODAL_TRANS_FREQ)
        self.__q0 = self.__preferences.get(MODAL_Q0)
        self.__f0 = self.__preferences.get(MODAL_F0)
        self.__modalCoeffs = self.__preferences.get(MODAL_COEFFS)
        self.__driverRadius = self.__preferences.get(MODAL_DRIVER_RADIUS)
        self.__measurementDistance = self.__preferences.get(MODAL_MEASUREMENT_DISTANCE)

    def reset(self):
        self.__preferences.clear_all(MODAL_GROUP)
        self.__init()

    def __repr__(self):
        return self.__class__.__name__

    def save(self):
        self.__preferences.set(MODAL_BOX_RADIUS, self.__boxRadius)
        self.__preferences.set(MODAL_LF_GAIN, self.__lfGain)
        self.__preferences.set(MODAL_TRANS_FREQ, self.__transFreq)
        self.__preferences.set(MODAL_Q0, self.__q0)
        self.__preferences.set(MODAL_F0, self.__f0)
        self.__preferences.set(MODAL_COEFFS, self.__modalCoeffs)
        self.__preferences.set(MODAL_DRIVER_RADIUS, self.__driverRadius)
        self.__preferences.set(MODAL_MEASUREMENT_DISTANCE, self.__measurementDistance)

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


class ModalParametersDialog(QDialog, Ui_modalParametersDialog):
    '''
    Modal Parameters dialog
    '''

    def __init__(self, parent, parameters, measurement_model, display_model):
        super(ModalParametersDialog, self).__init__(parent)
        self.setupUi(self)
        self.__parameters = parameters
        self.__measurement_model = measurement_model
        self.__display_model = display_model
        self.__load_values()
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.apply)
        self.buttonBox.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.reset)

    def __load_values(self):
        ''' Loads the values from the parameters. '''
        self.measurementDistance.setValue(self.__parameters.measurementDistance)
        self.driverRadius.setValue(self.__parameters.driverRadius * 100)
        self.modalCoeffs.setValue(self.__parameters.modalCoeffs)
        self.f0.setValue(self.__parameters.f0)
        self.q0.setValue(self.__parameters.q0)
        self.transFreq.setValue(self.__parameters.transFreq)
        self.lfGain.setValue(self.__parameters.lfGain)
        self.boxRadius.setValue(self.__parameters.boxRadius)

    def reset(self):
        ''' Resets the parameters '''
        self.__parameters.reset()
        self.__load_values()

    def apply(self):
        ''' Updates the parameters and reanalyses the model. '''
        logger.info('Updating modal parameters')
        self.__parameters.measurementDistance = self.measurementDistance.value()
        self.__parameters.driverRadius = self.driverRadius.value() / 100  # convert cm to m
        self.__parameters.modalCoeffs = self.modalCoeffs.value()
        self.__parameters.f0 = self.f0.value()
        self.__parameters.q0 = self.q0.value()
        self.__parameters.transFreq = self.transFreq.value()
        self.__parameters.lfGain = self.lfGain.value()
        self.__parameters.boxRadius = self.boxRadius.value()
        self.__parameters.save()
        from app import wait_cursor
        with wait_cursor('Applying modal parameter change'):
            self.__measurement_model.reanalyse()
            self.__display_model.redrawVisible()
