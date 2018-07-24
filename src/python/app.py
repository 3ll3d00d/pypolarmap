import sys

import matplotlib
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QDialog, QDialogButtonBox, QMessageBox

from model.load import WavLoader, HolmLoader, TxtLoader, DblLoader, REWLoader, ARTALoader
from model.measurement import REAL_WORLD_DATA, COMPUTED_MODAL_DATA
from model.multi import MultiChartModel
from model.polar import PolarModel
from ui.loadMeasurements import Ui_loadMeasurementDialog
from ui.pypolarmap import Ui_MainWindow

matplotlib.use("Qt5Agg")

from model import impulse as imp, magnitude as mag, contour, measurement as m, modal
from PyQt5 import QtCore, QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import colorcet as cc

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


class LoadMeasurementsDialog(QDialog, Ui_loadMeasurementDialog):
    '''
    Load Measurement dialog
    '''

    def __init__(self, parent=None):
        super(LoadMeasurementsDialog, self).__init__(parent)
        self.setupUi(self)
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Load")
        _translate = QtCore.QCoreApplication.translate
        self.fs.setCurrentText(_translate("loadMeasurementDialog", "48000"))
        self.__dialog = QFileDialog(parent=self)

    def accept(self):
        '''
        Shows the file select dialog based on the chosen options.
        :return:
        '''
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
        QDialog.accept(self)

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
                measurementModel.load(TxtLoader(selected[0], int(self.fs.currentText())).load())
            elif loadType == 'dbl':
                measurementModel.load(DblLoader(selected[0], int(self.fs.currentText())).load())
            elif loadType == 'wav':
                measurementModel.load(WavLoader(selected[0]).load())
            elif loadType == 'HolmImpulse':
                measurementModel.load(HolmLoader(selected[0]).load())
            elif loadType == 'REW':
                measurementModel.load(REWLoader(selected[0]).load())
            elif loadType == 'ARTA':
                measurementModel.load(ARTALoader(selected[0]).load())
        else:
            measurementModel.clear()
            dataPathField.setText('')

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

    def __init__(self, parent=None):
        super(PyPolarmap, self).__init__(parent)
        self.setupUi(self)
        self.loadColourMaps()
        self.dataPath.setDisabled(True)
        self._modalParameterModel = modal.ModalParameterModel(self.measurementDistance.value(),
                                                              self.driverRadius.value() / 100,
                                                              self.modalCoeffs.value(), self.f0.value(),
                                                              self.q0.value(),
                                                              self.transFreq.value(), self.lfGain.value(),
                                                              self.boxRadius.value())
        self._measurementModel = m.MeasurementModel(self._modalParameterModel)
        # modal graphs
        self._modalMultiModel = MultiChartModel(self.modalMultiGraph, self._measurementModel, COMPUTED_MODAL_DATA,
                                                dBRange=self.yAxisRange.value())
        self._modalPolarModel = modal.ContourModel(self.modalPolarGraph, self._measurementModel, COMPUTED_MODAL_DATA)
        # measured graphs
        self._measuredMultiModel = MultiChartModel(self.measuredMultiGraph, self._measurementModel, REAL_WORLD_DATA,
                                                   dBRange=self.yAxisRange.value())
        self._measuredPolarModel = contour.ContourModel(self.measuredPolarGraph, self._measurementModel,
                                                        type=REAL_WORLD_DATA)
        self._measuredMagnitudeModel = mag.MagnitudeModel(self.measuredMagnitudeGraph, self._measurementModel,
                                                          type=REAL_WORLD_DATA, dBRange=self.yAxisRange.value())
        # impulse graph
        self._impulseModel = imp.ImpulseModel(self.impulseGraph,
                                              {'position': self.leftWindowSample,
                                               'type': self.leftWindowType,
                                               'percent': self.leftWindowPercent},
                                              {'position': self.rightWindowSample,
                                               'type': self.rightWindowType,
                                               'percent': self.rightWindowPercent},
                                              self._measurementModel)
        self._measurementTableModel = m.MeasurementTableModel(self._measurementModel, parent=parent)
        self.measurementView.setModel(self._measurementTableModel)
        # TODO replace the show windowed button with a slider like https://stackoverflow.com/a/51023362/123054

    def loadColourMaps(self):
        _translate = QtCore.QCoreApplication.translate
        defaultIdx = 0
        for idx, (name, cm) in enumerate(cms_by_name.items()):
            self.colourMapSelector.addItem(_translate("MainWindow", name))
            if name == 'bgyw':
                defaultIdx = idx
        self.colourMapSelector.setCurrentIndex(defaultIdx)

    # signal handlers
    def selectDirectory(self):
        '''
        Triggered by the select directory button. Shows a file dialog which allows a user to select a directory which is
        used to load the set of measurements which is then passed to the various models.
        :return:
        '''
        dialog = LoadMeasurementsDialog(self)
        if dialog.exec():
            dialog.load(self._measurementModel, self.dataPath)
            if len(self._measurementModel) > 0:
                self.fs.setValue(self._measurementModel[0]._fs)
                self._measurementTableModel.completeRendering(self.measurementView)
                self.applyWindowBtn.setDisabled(False)
                self.removeWindowBtn.setDisabled(True)
                self.zoomInButton.setDisabled(False)
                self.zoomOutBtn.setDisabled(False)
            else:
                self.applyWindowBtn.setDisabled(True)
                self.removeWindowBtn.setDisabled(True)
                self.zoomInButton.setDisabled(True)
                self.zoomOutBtn.setDisabled(True)

    def getSelectedGraph(self):
        idx = self.graphTabs.currentIndex()
        if idx == 0:
            return self._impulseModel
        elif idx == 1:
            return self._measuredMagnitudeModel
        elif idx == 2:
            return self._measuredPolarModel
        elif idx == 3:
            return self._measuredMultiModel
        elif idx == 4:
            return self._modalPolarModel
        elif idx == 5:
            return self._modalMultiModel
        else:
            return None

    def onGraphTabChange(self):
        graph = self.getSelectedGraph()
        if graph is not None:
            display = getattr(graph, 'display', None)
            if display is not None and callable(display):
                display()

    def updateLeftWindowPosition(self):
        '''
        propagates left window changes to the impulse model.
        :return:
        '''
        self._impulseModel.updateLeftWindowPosition()

    def updateLeftWindowType(self):
        '''
        propagates left window changes to the impulse model.
        :return:
        '''
        # self._impulseModel.updateLeftWindowPosition()
        pass

    def updateLeftWindowPercentage(self):
        '''
        propagates left window changes to the impulse model.
        :return:
        '''
        # self._impulseModel.updateLeftWindowPosition()
        pass

    def updateLeftWindowPosition(self):
        '''
        propagates left window changes to the impulse model.
        :return:
        '''
        self._impulseModel.updateLeftWindowPosition()

    def updateRightWindowPosition(self):
        '''
        propagates right window changes to the impulse model.
        :return:
        '''
        self._impulseModel.updateRightWindowPosition()

    def updateRightWindowType(self):
        '''
        propagates right window changes to the impulse model.
        :return:
        '''
        # self._impulseModel.updateRightWindowPosition()
        pass

    def updateRightWindowPercentage(self):
        '''
        propagates right window changes to the impulse model.
        :return:
        '''
        # self._impulseModel.updateRightWindowPosition()
        pass

    def zoomIn(self):
        '''
        propagates the zoom button click to the impulse model.
        :return:
        '''
        self._impulseModel.zoomIn()

    def zoomOut(self):
        self._impulseModel.zoomOut()

    def removeWindow(self):
        '''
        propagates the window button click to the impulse model.
        :return:
        '''
        self.removeWindowBtn.setEnabled(False)
        self._impulseModel.removeWindow()
        self.zoomOut()

    def updateWindow(self):
        '''
        Propagates the button click to the model.
        '''
        self.removeWindowBtn.setEnabled(True)
        self._impulseModel.applyWindow()

    def updateColourMap(self, cmap):
        '''
        Updates the colour map in the charts.
        :param cmap: the named colour map.
        '''
        if hasattr(self, '_measuredPolarModel'):
            self._measuredPolarModel.updateColourMap(cmap)
            self._modalPolarModel.updateColourMap(cmap)

    def updateMeasurementDistance(self, value):
        '''
        propagates UI field to spatial model
        :param value: the value
        '''
        self._modalParameterModel.measurementDistance = value

    def updateDriverRadius(self, value):
        '''
        propagates UI field to spatial model
        :param value: the value
        '''
        self._modalParameterModel.driverRadius = value / 100  # convert cm to m

    def updateModalCoeffs(self, value):
        '''
        propagates UI field to spatial model
        :param value: the value
        '''
        self._modalParameterModel.modalCoeffs = value

    def updateF0(self, value):
        '''
        propagates UI field to spatial model
        :param value: the value
        '''
        self._modalParameterModel.f0 = value

    def updateQ0(self, value):
        '''
        propagates UI field to spatial model
        :param value: the value
        '''
        self._modalParameterModel.q0 = value

    def updateTransitionFrequency(self, value):
        '''
        propagates UI field to spatial model
        :param value: the value
        '''
        self._modalParameterModel.transFreq = value

    def updateLFGain(self, value):
        '''
        propagates UI field to spatial model
        :param value: the value
        '''
        self._modalParameterModel.lfGain = value

    def updateBoxRadius(self, value):
        '''
        propagates UI field to spatial model
        :param value: the value
        '''
        self._modalParameterModel.boxRadius = value

    def refreshModal(self):
        '''
        Tells the modal data to refresh.
        '''
        self._measurementModel.analyseModal()

    def updateSmoothing(self, smoothingType):
        '''
        Smooths the data in the measurement mode.
        :param smoothingType: the smoothing type.
        '''
        self._measurementModel.smooth(smoothingType)
        self.onGraphTabChange()

    def setYRange(self, yRange):
        '''
        Updates the y range for the displayed graphs.
        :param yRange:
        :return:
        '''
        selected = self.getSelectedGraph()
        self._update_db_range(self._modalMultiModel, selected, yRange)
        self._update_db_range(self._modalPolarModel, selected, yRange)
        self._update_db_range(self._measuredMagnitudeModel, selected, yRange)
        self._update_db_range(self._measuredMultiModel, selected, yRange)
        self._update_db_range(self._measuredPolarModel, selected, yRange)

    def _update_db_range(self, graph, selected, yRange):
        graph.updateDecibelRange(yRange, draw=graph is selected)

    def toggleNormalised(self, state):
        '''
        toggles whether to normalise the displayed data or not.
        :param state: normalisation selection.
        '''
        pass

    def setNormalisationAngle(self, angle):
        '''
        controls what the currently selected normalisation angle is.
        :param angle: the selected angle.
        '''
        pass


def main():
    app = QApplication(sys.argv)
    form = PyPolarmap()
    form.show()
    try:
        app.exec_()
    except:
        print("Error")


# add exception hook so we can find out why PyQt blows up
sys._excepthook = sys.excepthook


def dump_exception_to_log(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys.excepthook(exctype, value, traceback)
    sys.exit(1)


sys.excepthook = dump_exception_to_log

if __name__ == '__main__':
    main()
