import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

from model import impulse as imp
from model import magnitude as mag
from model import measurement as m
from ui import pypolarmap


class PyPolarmap(QMainWindow, pypolarmap.Ui_MainWindow):
    def __init__(self, parent=None):
        super(PyPolarmap, self).__init__(parent)
        self.setupUi(self)
        self.dataPath.setDisabled(True)
        self._magnitudeModel = mag.MagnitudeModel(self.magnitudeGraph)
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
                for g in self._graphs:
                    g.getPlotItem().clear()
                self.dataPath.setStyleSheet("QLineEdit {background-color: white;}")
                self.dataPath.setText(selectedDir[0])
                measurements = m.loadFromDir(selectedDir[0], 'txt')
                self._measurementModel.accept(measurements)
                self._measurementModel.completeRendering(self.measurementView)
                self._impulseModel.accept(measurements)
                self._impulseModel.display()
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
            self._impulseModel.display()
        elif idx == 1:
            self._magnitudeModel.display()
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
