import os
import re
import typing

import numpy as np
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant, QEvent
from PyQt5.QtWidgets import QItemDelegate


def asMeasurement(path, fileName, ext):
    '''
    Converts a file into a measurement object.
    :param path: the path to the file.
    :param fileName: the filename.
    :param ext: the extension.
    :return: the measurement if there is one.
    '''
    name = fileName[:len(ext) - 1]
    h = _getAngle(fileName, 'H')
    v = _getAngle(fileName, 'V')
    if h is not None:
        return Measurement(path, name, ext=ext, h=h)
    elif v is not None:
        return Measurement(path, name, ext=ext, v=v)
    else:
        return None  # ignore - filename format is invalid


def _getAngle(fileName, angle):
    '''
    Extracts the specified angle from the filename, expects angle to be embedded in the form _<ANGLE><DEGREES>
    :param fileName:
    :param angle:
    :return:
    '''
    matches = re.match('.*_?(' + angle + '([0-9]+)).*', fileName)
    if matches:
        return int(matches.group(2))
    else:
        return None


def loadFromDir(path, ext='txt'):
    '''
    Loads measurements from the specified dir
    :param path: the path the files are in.
    :param ext: the extension.
    :return: the measurements.
    '''
    return [x.load() for x in
            [asMeasurement(path, fileName, ext) for fileName in os.listdir(path) if fileName.endswith('.' + ext)] if
            x is not None]


def loadSamplesFromText(path):
    '''
    Loads samples from a text file that contains a single float per sample with 1 sample per line. The file must contain
    no other data.
    :param path: the path to the text file.
    :return: the samples as an ndarray.
    '''
    return np.genfromtxt(path, delimiter="\n")


class Measurement:
    '''
    Models a single measurement.
    '''

    def __init__(self, path, name, ext='txt', h=0, v=0):
        self._path = path
        self._name = name
        self._ext = ext
        self._h = h
        self._v = v
        self._active = True
        self.samples = np.array([])
        self._gated = None

    def load(self):
        # TODO support multiple load strategies (raw samples in txt, ARTA style space delimited, REW style text, WAV)
        self.samples = loadSamplesFromText(os.path.join(self._path, self._name + "." + self._ext))
        return self

    def size(self):
        return self.samples.size

    def min(self):
        return np.amin(self.samples)

    def max(self):
        return np.amax(self.samples)

    def peakIndex(self):
        return np.argmax(self.samples)

    def toggleState(self):
        self._active = not self._active
        if self._gated:
            self._gated._active = self._active

    def getDisplayName(self):
        return 'H' + str(self._h) + 'V' + str(self._v)

    def gated(self, left, right):
        '''
        Applies the left and right gate to the measurement.
        :param left: the left gate position.
        :param right: the right gate position.
        :return: a gated copy of this measurement.
        '''
        gated = Measurement(self._path, self._name, ext=self._ext, h=self._h, v=self._v)
        gated._active = self._active
        gated.samples = self.samples[left:right]
        self._gated = gated
        return gated


class MeasurementModel(QAbstractTableModel):
    '''
    A Qt table model to feed the measurements view. Accepts a listener for state changes.
    '''

    def __init__(self, parent=None, listener=None):
        super().__init__(parent=parent)
        self._headers = ['File', 'Type', 'Samples', 'H', 'V', 'Active']
        self._measurements = []
        self._listener = listener

    def rowCount(self, parent: QModelIndex = ...):
        return len(self._measurements)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self._headers)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if (index.column() == 5):
            return super().flags(index) | Qt.ItemIsEditable
        else:
            return super().flags(index)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        else:
            if index.column() == 0:
                return QVariant(self._measurements[index.row()]._name)
            elif index.column() == 1:
                return QVariant(self._measurements[index.row()]._ext)
            elif index.column() == 2:
                return QVariant(self._measurements[index.row()].size())
            elif index.column() == 3:
                return QVariant(self._measurements[index.row()]._h)
            elif index.column() == 4:
                return QVariant(self._measurements[index.row()]._v)
            elif index.column() == 5:
                return QVariant(self._measurements[index.row()]._active)
            else:
                return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self._headers[section])
        return QVariant()

    def accept(self, measurements):
        # TODO validate?
        self.layoutAboutToBeChanged.emit()
        self._measurements = measurements
        self.layoutChanged.emit()

    def completeRendering(self, view):
        view.setItemDelegateForColumn(5, CheckBoxDelegate(None))
        for x in range(0, 6):
            view.resizeColumnToContents(x)

    def toggleState(self, idx):
        self._measurements[idx].toggleState()
        if self._listener:
            self._listener.onMeasurementUpdate(idx)


# from https://stackoverflow.com/questions/17748546/pyqt-column-of-checkboxes-in-a-qtableview
class CheckBoxDelegate(QItemDelegate):
    """
    A delegate that places a fully functioning QCheckBox cell of the column to which it's applied & which propagates
    state changes to the owning measurement model.
    """

    def __init__(self, parent):
        QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        """
        Important, otherwise an editor is created if the user clicks in this cell.
        """
        return None

    def paint(self, painter, option, index):
        """
        Paint a checkbox without the label.
        """
        self.drawCheck(painter, option, option.rect, Qt.Unchecked if int(index.data()) == 0 else Qt.Checked)

    def editorEvent(self, event, model, option, index):
        '''
        Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton and this cell is editable. Otherwise do nothing.
        '''
        if not int(index.flags() & Qt.ItemIsEditable) > 0:
            return False

        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            # Change the checkbox-state
            model.toggleState(index.row())
            return True

        return False
