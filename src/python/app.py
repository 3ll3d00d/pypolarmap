import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

import matplotlib

matplotlib.use("Qt5Agg")

from model import impulse as imp, magnitude as mag, polar, measurement as m
from ui import pypolarmap
from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas


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
        QtWidgets.QWidget.__init__(self, parent)  # Inherit from QWidget
        self.canvas = MplCanvas()  # Create canvas object
        self.vbl = QtWidgets.QVBoxLayout()  # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)


class PyPolarmap(QMainWindow, pypolarmap.Ui_MainWindow):
    def __init__(self, parent=None):
        super(PyPolarmap, self).__init__(parent)
        self.setupUi(self)
        self.dataPath.setDisabled(True)
        self._polarModel = polar.PolarModel(self.polarGraph)
        self._magnitudeModel = mag.MagnitudeModel(self.magnitudeGraph, self._polarModel)
        self._impulseModel = imp.ImpulseModel(self.impulseGraph,
                                              left={'position': self.leftWindowSample,
                                                    'type': self.leftWindowType,
                                                    'percent': self.leftWindowPercent},
                                              right={'position': self.rightWindowSample,
                                                     'type': self.rightWindowType,
                                                     'percent': self.rightWindowPercent},
                                              mag=self._magnitudeModel)
        self._measurementModel = m.MeasurementModel(parent=parent, listener=self._impulseModel)
        self.measurementView.setModel(self._measurementModel)
        self._graphs = [self.impulseGraph, self.magnitudeGraph]

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
                # for g in self._graphs:
                #     g.getPlotItem().clear()
                self.dataPath.setStyleSheet("QLineEdit {background-color: white;}")
                self.dataPath.setText(selectedDir[0])
                measurements = m.loadFromDir(selectedDir[0], 'txt')
                self._measurementModel.accept(measurements)
                self._measurementModel.completeRendering(self.measurementView)
                self._impulseModel.accept(measurements)
                self._impulseModel.display()
                self._magnitudeModel.accept(measurements)
                self.toggleWindowedBtn.setDisabled(False)
                self.zoomButton.setDisabled(False)
            else:
                self._measurementModel.accept([])
                self._impulseModel.accept([])
                self._magnitudeModel.accept([])
                for g in self._graphs:
                    g.getPlotItem().clear()
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

    def zoomToWindow(self):
        '''
        propagates the zoom button click to the impulse model.
        :return:
        '''
        self._impulseModel.zoomToWindow()

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
