import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog

from model import measurement as m
from model import plot as p
from ui import pypolarmap


class PyPolarmap(QMainWindow, pypolarmap.Ui_MainWindow):
    def __init__(self, parent=None):
        super(PyPolarmap, self).__init__(parent)
        self.setupUi(self)
        self.dataPath.setDisabled(True)
        self.mainGraph.getPlotItem().showGrid(x=True, y=True, alpha=0.75)
        self._measurementModel = m.MeasurementModel(parent=parent)
        self._plotModel = p.PlotModel(self.mainGraph, self.leftWindowSample, self.rightWindowSample)
        self.measurementView.setModel(self._measurementModel)

    def selectDirectory(self):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.DirectoryOnly)
        dialog.setOption(QFileDialog.ShowDirsOnly)
        dialog.setWindowTitle("Load Measurements")
        if dialog.exec():
            selectedDir = dialog.selectedFiles()
            if len(selectedDir) > 0:
                self.dataPath.setStyleSheet("QLineEdit {background-color: white;}")
                self.dataPath.setText(selectedDir[0])
                measurements = m.loadFromDir(selectedDir[0], 'txt')
                self._measurementModel.accept(measurements)
                for x in range(0, 6):
                    self.measurementView.resizeColumnToContents(x)
                self._plotModel.accept(measurements)
                self._plotModel.displayImpulses()
            else:
                self._measurementModel.accept([])
                self._plotModel.accept([])

    def updateLeftWindowPosition(self):
        self._plotModel.updateLeftWindow()

    def updateLeftWindowType(self):
        pass

    def updateRightWindowPosition(self):
        self._plotModel.updateRightWindow()

    def updateRightWindowType(self):
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
