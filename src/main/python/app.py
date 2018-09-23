import logging
import math
import os
import sys
from contextlib import contextmanager

import matplotlib
from qtpy.QtCore import QSettings
from qtpy.QtGui import QIcon, QFont, QCursor
from qtpy.QtWidgets import QMainWindow, QFileDialog, QDialog, QDialogButtonBox, QMessageBox, QApplication, QErrorMessage

from model.contour import ContourModel
from model.display import DisplayModel, DisplayControlDialog
from model.load import WavLoader, HolmLoader, TxtLoader, DblLoader, REWLoader, ARTALoader
from model.log import RollingLogger
from model.measurement import REAL_WORLD_DATA, COMPUTED_MODAL_DATA
from model.modal import ModalParametersDialog
from model.multi import MultiChartModel
from model.preferences import Preferences
from ui.loadMeasurements import Ui_loadMeasurementDialog
from ui.pypolarmap import Ui_MainWindow
from ui.savechart import Ui_saveChartDialog

matplotlib.use("Qt5Agg")

from model import impulse as imp, magnitude as mag, measurement as m, modal
from qtpy import QtCore, QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import colorcet as cc

logger = logging.getLogger('pypolarmap')

# from http://colorcet.pyviz.org/index.html
inverse = {}
for k, v in cc.cm_n.items():
    if not k[-2:] == "_r":
        inverse[v] = inverse.get(v, [])
        inverse[v].insert(0, k)
all_cms = sorted({',  '.join(reversed(v)): k for (k, v) in inverse.items()}.items())
cms_by_name = dict(all_cms)


# Matplotlib canvas class to create figure
class MplCanvas(Canvas):
    def __init__(self):
        self.figure = Figure(tight_layout=True)
        Canvas.__init__(self, self.figure)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)


# Matplotlib widget
class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.vbl = QtWidgets.QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)
        self._cmap = self.getColourMap('rainbow')

    def getColourMap(self, name):
        return cms_by_name.get(name, cms_by_name.get('bgyw'))

    def getColour(self, idx, count):
        '''
        :param idx: the colour index.
        :return: the colour at that index.
        '''
        return self._cmap(idx / count)


class SaveChartDialog(QDialog, Ui_saveChartDialog):
    '''
    Save Chart dialog
    '''

    def __init__(self, parent, selectedGraph, statusbar):
        super(SaveChartDialog, self).__init__(parent)
        self.setupUi(self)
        self.chart = selectedGraph
        fig = self.chart._chart.canvas.figure
        self.__dpi = fig.dpi
        self.__x, self.__y = fig.get_size_inches() * fig.dpi
        self.__aspectRatio = self.__x / self.__y
        self.widthPixels.setValue(self.__x)
        self.heightPixels.setValue(self.__y)
        self.statusbar = statusbar
        self.__dialog = QFileDialog(parent=self)

    def accept(self):
        formats = "Portable Network Graphic (*.png)"
        fileName = self.__dialog.getSaveFileName(self, 'Export Chart', f"{self.chart.name}.png", formats)
        if fileName:
            outputFile = str(fileName[0]).strip()
            if len(outputFile) == 0:
                return
            else:
                scaleFactor = self.widthPixels.value() / self.__x
                self.chart._chart.canvas.figure.savefig(outputFile, format='png', dpi=self.__dpi * scaleFactor)
                self.statusbar.showMessage(f"Saved {self.chart.name} to {outputFile}", 5000)
        QDialog.accept(self)

    def updateHeight(self, newWidth):
        '''
        Updates the height as the width changes according to the aspect ratio.
        :param newWidth: the new width.
        '''
        self.heightPixels.setValue(int(math.floor(newWidth / self.__aspectRatio)))


class LoadMeasurementsDialog(QDialog, Ui_loadMeasurementDialog):
    '''
    Load Measurement dialog
    '''

    def __init__(self, parent=None):
        super(LoadMeasurementsDialog, self).__init__(parent)
        self.setupUi(self)
        self.buttonBox.button(QDialogButtonBox.Open).setText("Select File(s)")
        _translate = QtCore.QCoreApplication.translate
        self.fs.setCurrentText(_translate("loadMeasurementDialog", "48000"))
        self.__dialog = QFileDialog(parent=self)
        self.__errors = 0

    def accept(self):
        '''
        Shows the file select dialog based on the chosen options.
        :return:
        '''
        self.__errors = 0
        self.loadedFiles.clear()
        self.ignoredFiles.clear()
        loadType = self.fileType.currentText()
        fileMode = None
        option = QFileDialog.ShowDirsOnly
        if loadType == 'txt' or loadType == 'dbl':
            fileMode = QFileDialog.DirectoryOnly
        elif loadType == 'wav':
            fileMode = QFileDialog.DirectoryOnly
        elif loadType == 'HolmImpulse':
            fileMode = QFileDialog.ExistingFile
            option = QFileDialog.DontConfirmOverwrite
        elif loadType == 'REW':
            fileMode = QFileDialog.DirectoryOnly
        elif loadType == 'ARTA':
            fileMode = QFileDialog.DirectoryOnly
        else:
            QMessageBox.about(self, "Error", "Unknown format " + loadType)
        if fileMode is not None:
            self.__dialog.setFileMode(fileMode)
            self.__dialog.setOption(option)
            self.__dialog.setWindowTitle("Load Measurements")
            self.__dialog.exec()

    def load(self, measurementModel, dataPathField):
        '''
        Loads the measurements by looking in the selected directory.
        :param measurementModel: the model to load.
        :param dataPathField: the display field.
        :return:
        '''
        selected = self.__dialog.selectedFiles()
        loadType = self.fileType.currentText()
        if len(selected) > 0:
            dataPathField.setText(selected[0])
            if loadType == 'txt':
                measurementModel.load(TxtLoader(self.onFile, selected[0], int(self.fs.currentText())).load())
            elif loadType == 'dbl':
                measurementModel.load(DblLoader(self.onFile, selected[0], int(self.fs.currentText())).load())
            elif loadType == 'wav':
                measurementModel.load(WavLoader(self.onFile, selected[0]).load())
            elif loadType == 'HolmImpulse':
                measurementModel.load(HolmLoader(self.onFile, selected[0]).load())
            elif loadType == 'REW':
                measurementModel.load(REWLoader(self.onFile, selected[0]).load())
            elif loadType == 'ARTA':
                measurementModel.load(ARTALoader(self.onFile, selected[0]).load())
        else:
            measurementModel.clear()
            dataPathField.setText('')
        if self.__errors == 0:
            QDialog.accept(self)

    def onFile(self, filename, loaded):
        if loaded is True:
            self.loadedFiles.appendPlainText(filename)
        else:
            self.ignoredFiles.appendPlainText(filename)
            self.__errors += 1

    def fileTypeChanged(self, text):
        '''
        Hides the fs field if the fs is determined by the source file.
        :param text: the selected text.
        '''
        visible = True
        if text == 'txt' or text == 'dbl':
            pass
        else:
            visible = False
        self.fs.setVisible(visible)
        self.fsLabel.setVisible(visible)


class PyPolarmap(QMainWindow, Ui_MainWindow):
    '''
    The main UI.
    '''

    def __init__(self, app, parent=None):
        super(PyPolarmap, self).__init__(parent)
        self.app = app
        self.preferences = Preferences(QSettings("3ll3d00d", "beqdesigner"))
        self.setupUi(self)
        self.logViewer = RollingLogger(self, self.preferences)
        self.logger = logging.getLogger('pypolarmap')
        if getattr(sys, 'frozen', False):
            self.__root_path = sys._MEIPASS
        else:
            self.__root_path = os.path.dirname(__file__)
        self.__version = 'UNKNOWN'
        try:
            with open(os.path.join(self.__root_path, 'VERSION')) as version_file:
                self.__version = version_file.read().strip()
        except:
            logger.exception('Unable to load version')
        # menus
        self.actionLoad.triggered.connect(self.selectDirectory)
        self.actionSave_Current_Image.triggered.connect(self.saveCurrentChart)
        self.actionShow_Logs.triggered.connect(self.logViewer.show_logs)
        self.actionAbout.triggered.connect(self.showAbout)
        self.dataPath.setDisabled(True)
        self.__modal_parameter_model = modal.ModalParameterModel(self.preferences)
        self.__display_model = DisplayModel(self.preferences)
        self.__measurement_model = m.MeasurementModel(self.__modal_parameter_model, self.__display_model)
        # modal graphs
        self.__modal_multi_model = MultiChartModel(self.modalMultiGraph, self.__measurement_model, COMPUTED_MODAL_DATA,
                                                   self.__display_model)
        self.__modal_polar_model = ContourModel(self.modalPolarGraph, self.__measurement_model, COMPUTED_MODAL_DATA,
                                                self.__display_model)
        # measured graphs
        self.__measured_multi_model = MultiChartModel(self.measuredMultiGraph, self.__measurement_model,
                                                      REAL_WORLD_DATA, self.__display_model)
        self.__measured_polar_model = ContourModel(self.measuredPolarGraph, self.__measurement_model,
                                                   REAL_WORLD_DATA, self.__display_model)
        self.__measured_magnitude_model = mag.MagnitudeModel(self.measuredMagnitudeGraph, self.__measurement_model,
                                                             self.__display_model, type=REAL_WORLD_DATA)
        self.__display_model.results_charts = [self.__modal_multi_model, self.__modal_polar_model,
                                               self.__measured_multi_model, self.__measured_polar_model,
                                               self.__measured_magnitude_model]
        # impulse graph
        self.__impulse_model = imp.ImpulseModel(self.impulseGraph,
                                                {'position': self.leftWindowSample,
                                                 'type': self.leftWindowType,
                                                 'percent': self.leftWindowPercent},
                                                {'position': self.rightWindowSample,
                                                 'type': self.rightWindowType,
                                                 'percent': self.rightWindowPercent},
                                                self.__measurement_model)
        self.__measurement_list_model = m.MeasurementListModel(self.__measurement_model, parent=parent)
        self.measurementView.setModel(self.__measurement_list_model)
        # TODO replace the show windowed button with a slider like https://stackoverflow.com/a/51023362/123054
        self.actionModal_Parameters.triggered.connect(self.show_modal_parameters_dialog)
        self.action_Display.triggered.connect(self.show_display_controls_dialog)
        self.graphTabs.setEnabled(False)

    def showAbout(self):
        ''' Shows the about dialog '''
        msg_box = QMessageBox()
        msg_box.setText(
            f"<a href='https://github.com/3ll3d00d/pypolarmap'>pypolarmap</a> v{self.__version} by 3ll3d00d")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle('About')
        msg_box.exec()

    def show_modal_parameters_dialog(self):
        '''
        Shows the parameters dialog.
        '''
        ModalParametersDialog(self, self.__modal_parameter_model, self.__measurement_model).show()

    def show_display_controls_dialog(self):
        '''
        Shows the parameters dialog.
        '''
        DisplayControlDialog(self, self.__display_model, self.__measurement_model).show()

    def setupUi(self, mainWindow):
        super().setupUi(self)
        geometry = self.preferences.get("geometry")
        if not geometry == None:
            self.restoreGeometry(geometry)
        else:
            screenGeometry = self.app.desktop().availableGeometry()
            if screenGeometry.height() < 800:
                self.showMaximized()
        windowState = self.preferences.get("windowState")
        if not windowState == None:
            self.restoreState(windowState)

    def closeEvent(self, *args, **kwargs):
        '''
        Saves the window state on close.
        :param args:
        :param kwargs:
        '''
        self.preferences.set("geometry", self.saveGeometry())
        self.preferences.set("windowState", self.saveState())
        super().closeEvent(*args, **kwargs)
        self.app.closeAllWindows()

    # signal handlers
    def selectDirectory(self):
        '''
        Triggered by the select directory button. Shows a file dialog which allows a user to select a directory which is
        used to load the set of measurements which is then passed to the various models.
        :return:
        '''
        dialog = LoadMeasurementsDialog(self)
        # this is a bit weird but it saves moving all of these references to assorted gui objects into the dialog
        # it is required because we want the dialog to stay open if there are errors
        wrapper = self

        def _trigger_load():
            dialog.load(wrapper.__measurement_model, wrapper.dataPath)
            if len(wrapper.__measurement_model) > 0:
                wrapper.fs.setValue(wrapper.__measurement_model[0]._fs)
                wrapper.__measurement_list_model.completeRendering(wrapper.measurementView)
                wrapper.graphTabs.setEnabled(True)
                wrapper.disable_analysed_tabs()
            else:
                wrapper.graphTabs.setEnabled(False)

        dialog.buttonBox.accepted.connect(_trigger_load)
        result = dialog.exec()

    def saveCurrentChart(self):
        '''
        Saves the currently selected chart to a file.
        '''
        selectedGraph = self.getSelectedGraph()
        dialog = SaveChartDialog(self, selectedGraph, self.statusbar)
        dialog.exec()

    def getSelectedGraph(self):
        idx = self.graphTabs.currentIndex()
        if idx == 0:
            return self.__impulse_model
        elif idx == 1:
            return self.__measured_magnitude_model
        elif idx == 2:
            return self.__measured_polar_model
        elif idx == 3:
            return self.__measured_multi_model
        elif idx == 4:
            return self.__modal_polar_model
        elif idx == 5:
            return self.__modal_multi_model
        else:
            return None

    def onGraphTabChange(self):
        '''
        Updates the visible chart.
        '''
        self.__display_model.visibleChart = self.getSelectedGraph()

    def updateLeftWindow(self):
        ''' propagates left window changes to the impulse model. '''
        self.__impulse_model.updateLeftWindow()
        self.applyWindowBtn.setEnabled(self.__impulse_model.is_window_valid())

    def updateRightWindow(self):
        ''' propagates right window changes to the impulse model. '''
        self.__impulse_model.updateRightWindow()
        self.applyWindowBtn.setEnabled(self.__impulse_model.is_window_valid())

    def zoomIn(self):
        ''' propagates the zoom button click to the impulse model. '''
        self.__impulse_model.zoomIn()

    def zoomOut(self):
        ''' Propagates the zoom button click to the impulse model. '''
        self.__impulse_model.zoomOut()

    def findFirstPeak(self):
        ''' Propagates the find peaks button click to the impulse model. '''
        self.__impulse_model.findFirstPeak()

    def removeWindow(self):
        ''' propagates the window button click to the impulse model. '''
        self.removeWindowBtn.setEnabled(False)
        self.__impulse_model.removeWindow()
        self.zoomOut()
        self.disable_analysed_tabs()

    def updateWindow(self):
        ''' Propagates the button click to the model. '''
        self.removeWindowBtn.setEnabled(True)
        self.__impulse_model.applyWindow()
        self.enable_analysed_tabs()

    def disable_analysed_tabs(self):
        ''' Enables all tabs that depend on the impulse analysis '''
        for idx in range(1, self.graphTabs.count()):
            self.graphTabs.setTabEnabled(idx, False)

    def enable_analysed_tabs(self):
        ''' Enables all tabs that depend on the impulse analysis '''
        for idx in range(1, self.graphTabs.count()):
            self.graphTabs.setTabEnabled(idx, True)


e_dialog = None


def main():
    app = QApplication(sys.argv)
    if getattr(sys, 'frozen', False):
        iconPath = os.path.join(sys._MEIPASS, 'Icon.ico')
    else:
        iconPath = os.path.abspath(os.path.join(os.path.dirname('__file__'), '../icons/Icon.ico'))
    if os.path.exists(iconPath):
        app.setWindowIcon(QIcon(iconPath))
    form = PyPolarmap(app)
    # setup the error handler
    global e_dialog
    e_dialog = QErrorMessage(form)
    e_dialog.setWindowModality(QtCore.Qt.WindowModal)
    font = QFont()
    font.setFamily("Consolas")
    font.setPointSize(8)
    e_dialog.setFont(font)
    form.show()
    app.exec_()


# display exceptions in a QErrorMessage so the user knows what just happened
sys._excepthook = sys.excepthook


def dump_exception_to_log(exctype, value, tb):
    import traceback
    if e_dialog is not None:
        formatted = traceback.format_exception(etype=exctype, value=value, tb=tb)
        msg = '<br>'.join(formatted)
        e_dialog.setWindowTitle('Unexpected Error')
        e_dialog.showMessage(msg)
        e_dialog.resize(1200, 400)
    else:
        print(exctype, value, tb)


sys.excepthook = dump_exception_to_log

if __name__ == '__main__':
    main()


@contextmanager
def wait_cursor(msg=None):
    '''
    Allows long running functions to show a busy cursor.
    :param msg: a message to put in the status bar.
    '''
    try:
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
        yield
    finally:
        QApplication.restoreOverrideCursor()
