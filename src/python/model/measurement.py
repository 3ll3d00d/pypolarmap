import os
import re
import typing

import numpy as np
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant


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
    if h:
        return Measurement(path, name, ext=ext, h=h)
    elif v:
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
        self.samples = np.array([])

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


class MeasurementModel(QAbstractTableModel):
    '''
    A Qt table model to feed the measurements view.
    '''

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._headers = ['File', 'Type', 'Samples', 'H', 'V', 'Active']
        self._measurements = []

    def rowCount(self, parent: QModelIndex = ...):
        return len(self._measurements)

    def columnCount(self, parent: QModelIndex = ...):
        return len(self._headers)

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
                return QVariant(True)
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
