from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from model.preferences import DISPLAY_DB_RANGE, DISPLAY_COLOUR_MAP, DISPLAY_POLAR_360
from ui.display import Ui_displayControlsDialog


class DisplayModel:
    '''
    Parameters to feed into how a chart should be displayed.
    '''

    def __init__(self, preferences):
        self.__preferences = preferences
        self.__dBRange = self.__preferences.get(DISPLAY_DB_RANGE)
        self.__normalised = False
        self.__normalisationAngle = 0
        self.__visibleChart = None
        self.__colour_map = self.__preferences.get(DISPLAY_COLOUR_MAP)
        self.__smoothing_type = None
        self.__locked = False
        self.__full_polar_range = self.__preferences.get(DISPLAY_POLAR_360)
        self.results_charts = []
        self.measurement_model = None

    def __repr__(self):
        return self.__class__.__name__

    @property
    def colour_map(self):
        return self.__colour_map

    @colour_map.setter
    def colour_map(self, colour_map):
        self.__colour_map = colour_map
        for chart in self.results_charts:
            if hasattr(chart, 'updateColourMap'):
                chart.updateColourMap(self.__colour_map, draw=chart is self.__visibleChart)
        self.__preferences.set(DISPLAY_COLOUR_MAP, colour_map)

    @property
    def dBRange(self):
        return self.__dBRange

    @dBRange.setter
    def dBRange(self, dBRange):
        self.__dBRange = dBRange
        for chart in self.results_charts:
            chart.updateDecibelRange(draw=chart is self.__visibleChart)
        self.__preferences.set(DISPLAY_DB_RANGE, dBRange)

    @property
    def smoothing_type(self):
        return self.__smoothing_type

    @smoothing_type.setter
    def smoothing_type(self, smoothing_type):
        self.__smoothing_type = smoothing_type
        self.measurement_model.smooth(self.__smoothing_type)

    @property
    def normalised(self):
        return self.__normalised

    @normalised.setter
    def normalised(self, normalised):
        self.__normalised = normalised
        self.measurement_model.normalisationChanged()
        self.redrawVisible()

    @property
    def normalisationAngle(self):
        return self.__normalisationAngle

    @normalisationAngle.setter
    def normalisationAngle(self, normalisationAngle):
        changed = normalisationAngle != self.__normalisationAngle
        self.__normalisationAngle = normalisationAngle
        if changed and self.__normalised:
            self.measurement_model.normalisationChanged()
            self.redrawVisible()

    @property
    def full_polar_range(self):
        return self.__full_polar_range

    @full_polar_range.setter
    def full_polar_range(self, full_polar_range):
        changed = full_polar_range != self.__full_polar_range
        self.__full_polar_range = full_polar_range
        if changed:
            self.redrawVisible()

    @property
    def visibleChart(self):
        return self.__visibleChart

    @visibleChart.setter
    def visibleChart(self, visibleChart):
        if self.__visibleChart is not None and getattr(self.__visibleChart, 'hide', None) is not None:
            self.__visibleChart.hide()
        self.__visibleChart = visibleChart
        self.redrawVisible()

    def redrawVisible(self):
        if self.__visibleChart is not None and self.__locked is not True:
            display = getattr(self.__visibleChart, 'display', None)
            if display is not None and callable(display):
                display()

    def lock(self):
        ''' flags the model as locked so changes do not result in a redraw '''
        self.__locked = True

    def unlock(self):
        ''' flags the model as unlocked and redraws '''
        self.__locked = False
        self.redrawVisible()


class DisplayControlDialog(QDialog, Ui_displayControlsDialog):
    '''
    Display Parameters dialog
    '''

    def __init__(self, parent, display_model, measurement_model):
        super(DisplayControlDialog, self).__init__(parent)
        self.setupUi(self)
        self.__display_model = display_model
        self.__measurement_model = measurement_model
        self.yAxisRange.setValue(self.__display_model.dBRange)
        self.normaliseCheckBox.setChecked(self.__display_model.normalised)
        self.__select_combo(self.smoothingType, self.__display_model.smoothing_type)
        for m in self.__measurement_model:
            self.normalisationAngle.addItem(str(m.h))
        if not self.__select_combo(self.normalisationAngle, str(self.__display_model.normalisationAngle)):
            self.__display_model.normalisationAngle = None
        stored_idx = 0
        from app import cms_by_name
        for idx, (name, cm) in enumerate(cms_by_name.items()):
            self.colourMapSelector.addItem(name)
            if name == self.__display_model.colour_map:
                stored_idx = idx
        self.colourMapSelector.setCurrentIndex(stored_idx)
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.apply)

    def __select_combo(self, combo, value):
        if value is not None:
            idx = combo.findText(value)
            if idx != -1:
                combo.setCurrentIndex(idx)
                return idx
        return None

    def apply(self):
        ''' Updates the parameters and reanalyses the model. '''
        from app import wait_cursor
        with wait_cursor():
            self.__display_model.lock()
            self.__display_model.smoothing_type = self.smoothingType.currentText()
            self.__display_model.dBRange = self.yAxisRange.value()
            self.__display_model.normalised = self.normaliseCheckBox.isChecked()
            self.__display_model.normalisationAngle = self.normalisationAngle.currentText()
            self.__display_model.colour_map = self.colourMapSelector.currentText()
            self.__display_model.unlock()
