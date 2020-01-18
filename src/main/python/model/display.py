from PyQt5.QtWidgets import QDialog, QDialogButtonBox

from model.preferences import DISPLAY_DB_RANGE, DISPLAY_COLOUR_MAP, DISPLAY_POLAR_360
from ui.display import Ui_displayControlsDialog


class DisplayModel:
    '''
    Parameters to feed into how a chart should be displayed.
    '''

    def __init__(self, preferences):
        self.__preferences = preferences
        self.__db_range = self.__preferences.get(DISPLAY_DB_RANGE)
        self.__normalised = False
        self.__normalisation_angle = 0
        self.__visible_chart = None
        self.__colour_map = self.__preferences.get(DISPLAY_COLOUR_MAP)
        self.__locked = False
        self.__full_polar_range = self.__preferences.get(DISPLAY_POLAR_360)
        self.results_charts = []
        self.measurement_model = None

    def __repr__(self):
        return self.__class__.__name__

    @property
    def colour_map(self):
        return self.__colour_map

    def accept(self, colour_map, db_range, is_normalised, normalisation_angle, full_polar_range):
        self.lock()
        should_refresh = False
        norm_change = False
        if self.__colour_map != colour_map:
            self.__colour_map = colour_map
            for chart in self.results_charts:
                if hasattr(chart, 'update_colour_map'):
                    chart.update_colour_map(self.__colour_map, draw=False)
            self.__preferences.set(DISPLAY_COLOUR_MAP, colour_map)
            should_refresh = True

        if self.__db_range != db_range:
            for chart in self.results_charts:
                chart.update_decibel_range(draw=False)
            self.__preferences.set(DISPLAY_DB_RANGE, db_range)
            should_refresh = True

        if self.__normalised != is_normalised:
            self.__normalised = is_normalised
            should_refresh = True
            norm_change = True

        if full_polar_range != self.__full_polar_range:
            self.__full_polar_range = full_polar_range
            should_refresh = True

        if normalisation_angle != self.__normalisation_angle:
            self.__normalisation_angle = normalisation_angle
            if self.__normalised:
                norm_change = True
                should_refresh = True

        if norm_change:
            self.measurement_model.normalisation_changed()

        self.unlock(should_refresh)

    @property
    def db_range(self):
        return self.__db_range

    @property
    def normalised(self):
        return self.__normalised

    @property
    def normalisation_angle(self):
        return self.__normalisation_angle

    @property
    def full_polar_range(self):
        return self.__full_polar_range

    @property
    def visible_chart(self):
        return self.__visible_chart

    @visible_chart.setter
    def visible_chart(self, visible_chart):
        if self.__visible_chart is not None and getattr(self.__visible_chart, 'hide', None) is not None:
            self.__visible_chart.hide()
        self.__visible_chart = visible_chart
        self.redraw_visible()

    def redraw_visible(self):
        if self.__visible_chart is not None and self.__locked is not True:
            display = getattr(self.__visible_chart, 'display', None)
            if display is not None and callable(display):
                display()

    def lock(self):
        ''' flags the model as locked so changes do not result in a redraw '''
        self.__locked = True

    def unlock(self, should_redraw):
        ''' flags the model as unlocked and redraws '''
        self.__locked = False
        if should_redraw:
            self.redraw_visible()


class DisplayControlDialog(QDialog, Ui_displayControlsDialog):
    '''
    Display Parameters dialog
    '''

    def __init__(self, parent, display_model, measurement_model):
        super(DisplayControlDialog, self).__init__(parent)
        self.setupUi(self)
        self.__display_model = display_model
        self.__measurement_model = measurement_model
        self.yAxisRange.setValue(self.__display_model.db_range)
        self.normaliseCheckBox.setChecked(self.__display_model.normalised)
        for m in self.__measurement_model:
            self.normalisationAngle.addItem(str(m.h))
        self.__select_combo(self.normalisationAngle, str(self.__display_model.normalisation_angle))
        stored_idx = 0
        from app import cms_by_name
        for idx, (name, cm) in enumerate(cms_by_name.items()):
            self.colourMapSelector.addItem(name)
            if name == self.__display_model.colour_map:
                stored_idx = idx
        self.colourMapSelector.setCurrentIndex(stored_idx)
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.apply)

    @staticmethod
    def __select_combo(combo, value):
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
            self.__display_model.accept(self.colourMapSelector.currentText(),
                                        self.yAxisRange.value(),
                                        self.normaliseCheckBox.isChecked(),
                                        self.normalisationAngle.currentText(),
                                        self.polarRange.isChecked())
