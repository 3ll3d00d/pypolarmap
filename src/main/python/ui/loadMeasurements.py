# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'loadMeasurements.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_loadMeasurementDialog(object):
    def setupUi(self, loadMeasurementDialog):
        loadMeasurementDialog.setObjectName("loadMeasurementDialog")
        loadMeasurementDialog.resize(482, 170)
        loadMeasurementDialog.setModal(True)
        self.buttonBox = QtWidgets.QDialogButtonBox(loadMeasurementDialog)
        self.buttonBox.setGeometry(QtCore.QRect(120, 120, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayoutWidget = QtWidgets.QWidget(loadMeasurementDialog)
        self.formLayoutWidget.setGeometry(QtCore.QRect(19, 20, 441, 81))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.fileType = QtWidgets.QComboBox(self.formLayoutWidget)
        self.fileType.setObjectName("fileType")
        self.fileType.addItem("")
        self.fileType.addItem("")
        self.fileType.addItem("")
        self.fileType.addItem("")
        self.fileType.addItem("")
        self.fileType.addItem("")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.fileType)
        self.fsLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.fsLabel.setObjectName("fsLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.fsLabel)
        self.fs = QtWidgets.QComboBox(self.formLayoutWidget)
        self.fs.setObjectName("fs")
        self.fs.addItem("")
        self.fs.addItem("")
        self.fs.addItem("")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.fs)

        self.retranslateUi(loadMeasurementDialog)
        self.buttonBox.accepted.connect(loadMeasurementDialog.accept)
        self.buttonBox.rejected.connect(loadMeasurementDialog.reject)
        self.fileType.currentIndexChanged['QString'].connect(loadMeasurementDialog.fileTypeChanged)
        QtCore.QMetaObject.connectSlotsByName(loadMeasurementDialog)

    def retranslateUi(self, loadMeasurementDialog):
        _translate = QtCore.QCoreApplication.translate
        loadMeasurementDialog.setWindowTitle(_translate("loadMeasurementDialog", "Load Measurements"))
        self.label_2.setText(_translate("loadMeasurementDialog", "File Type"))
        self.fileType.setItemText(0, _translate("loadMeasurementDialog", "txt"))
        self.fileType.setItemText(1, _translate("loadMeasurementDialog", "dbl"))
        self.fileType.setItemText(2, _translate("loadMeasurementDialog", "wav"))
        self.fileType.setItemText(3, _translate("loadMeasurementDialog", "HolmImpulse"))
        self.fileType.setItemText(4, _translate("loadMeasurementDialog", "REW"))
        self.fileType.setItemText(5, _translate("loadMeasurementDialog", "ARTA"))
        self.fsLabel.setText(_translate("loadMeasurementDialog", "Fs"))
        self.fs.setCurrentText(_translate("loadMeasurementDialog", "48000"))
        self.fs.setItemText(0, _translate("loadMeasurementDialog", "44100"))
        self.fs.setItemText(1, _translate("loadMeasurementDialog", "48000"))
        self.fs.setItemText(2, _translate("loadMeasurementDialog", "96000"))

