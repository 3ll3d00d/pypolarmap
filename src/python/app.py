import sys

import matplotlib
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

matplotlib.use("Qt5Agg")

from model import impulse as imp, magnitude as mag, polar, measurement as m
from ui import pypolarmap
from PyQt5 import QtCore, QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib.pyplot as plt

colourMaps = sorted((m for m in plt.colormaps() if not m.endswith("_r")), key=str.lower)


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
        self._cmap = plt.cm.get_cmap('tab20')

    def getColourMap(self, name):
        return plt.cm.get_cmap(name)

    def getColour(self, idx):
        '''
        :param idx: the colour index.
        :return: the colour at that index.
        '''
        cIdx = idx if idx == 0 or idx < len(self._cmap.colors) else len(self._cmap.colors) % idx
        return self._cmap.colors[cIdx]


class PyPolarmap(QMainWindow, pypolarmap.Ui_MainWindow):
    def __init__(self, parent=None):
        super(PyPolarmap, self).__init__(parent)
        self.setupUi(self)
        self.loadColourMaps()
        self.dataPath.setDisabled(True)
        self._measurementModel = m.MeasurementModel()
        self._polarModel = polar.PolarModel(self.polarGraph, self._measurementModel, self.contourInterval.value())
        self._magnitudeModel = mag.MagnitudeModel(self.magnitudeGraph, self._measurementModel, self._polarModel)
        self._impulseModel = imp.ImpulseModel(self.impulseGraph,
                                              {'position': self.leftWindowSample,
                                               'type': self.leftWindowType,
                                               'percent': self.leftWindowPercent},
                                              {'position': self.rightWindowSample,
                                               'type': self.rightWindowType,
                                               'percent': self.rightWindowPercent},
                                              self._measurementModel,
                                              self._magnitudeModel)
        self._measurementTableModel = m.MeasurementTableModel(self._measurementModel, parent=parent)
        self.measurementView.setModel(self._measurementTableModel)
        self._graphs = [self.impulseGraph, self.magnitudeGraph]

    def loadColourMaps(self):
        _translate = QtCore.QCoreApplication.translate
        defaultIdx = 0
        for idx, cm in enumerate(colourMaps):
            self.colourMapSelector.addItem(_translate("MainWindow", cm))
            if cm == 'plasma':
                defaultIdx = idx
        self.colourMapSelector.setCurrentIndex(defaultIdx)

    # signal handlers
    def selectDirectory(self):
        '''
        Triggered by the select directory button. Shows a file dialog which allows a user to select a directory which is
        used to load the set of measurements which is then passed to the various models.
        :return:
        '''
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setOption(QFileDialog.ShowDirsOnly)
        dialog.setWindowTitle("Load Measurements")
        if dialog.exec():
            selectedDir = dialog.selectedFiles()
            if len(selectedDir) > 0:
                self.dataPath.setStyleSheet("QLineEdit {background-color: white;}")
                self.dataPath.setText(selectedDir[0])
                self._measurementModel.load(selectedDir)
                self._measurementTableModel.completeRendering(self.measurementView)
                self.toggleWindowedBtn.setDisabled(False)
                self.zoomButton.setDisabled(False)
            else:
                self._measurementModel.clear()
                self.toggleWindowedBtn.setDisabled(True)
                self.zoomButton.setDisabled(True)

    def onGraphTabChange(self):
        idx = self.graphTabs.currentIndex()
        if idx == 0:
            # self._impulseModel.display()
            pass
        elif idx == 1:
            self._magnitudeModel.display()
        elif idx == 2:
            self._polarModel.display()
        else:
            # unknown
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

    def zoomIn(self):
        '''
        propagates the zoom button click to the impulse model.
        :return:
        '''
        self._impulseModel.zoomIn()

    def zoomOut(self):
        self._impulseModel.zoomOut()

    def toggleWindowed(self):
        '''
        propagates the window button click to the impulse model.
        :return:
        '''
        if self.toggleWindowedBtn.isChecked():
            self.toggleWindowedBtn.setText('Show Windowed IR')
        else:
            self.toggleWindowedBtn.setText('Show Raw IR')
        self._impulseModel.toggleWindowed()

    def updateWindow(self):
        '''
        Propagates the button click to the model.
        '''
        self._impulseModel.updateWindow()

    def updateColourMap(self, cmap):
        '''
        Updates the colour map in the charts.
        :param cmap: the named colour map.
        '''
        if hasattr(self, '_polarModel'):
            self._polarModel.updateColourMap(cmap)

    def updateContourInterval(self, interval):
        '''
        Redraws the contours with the new interval.
        :param interval:  the interval.
        '''
        self._polarModel.updateContourInterval(interval)


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
