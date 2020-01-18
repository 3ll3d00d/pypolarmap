# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'display.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_displayControlsDialog(object):
    def setupUi(self, displayControlsDialog):
        displayControlsDialog.setObjectName("displayControlsDialog")
        displayControlsDialog.resize(302, 188)
        self.gridLayout = QtWidgets.QGridLayout(displayControlsDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(displayControlsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.colourSchemeLabel = QtWidgets.QLabel(displayControlsDialog)
        self.colourSchemeLabel.setObjectName("colourSchemeLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.colourSchemeLabel)
        self.colourMapSelector = QtWidgets.QComboBox(displayControlsDialog)
        self.colourMapSelector.setObjectName("colourMapSelector")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.colourMapSelector)
        self.decibelRangeLabel = QtWidgets.QLabel(displayControlsDialog)
        self.decibelRangeLabel.setObjectName("decibelRangeLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.decibelRangeLabel)
        self.yAxisRange = QtWidgets.QSpinBox(displayControlsDialog)
        self.yAxisRange.setMinimum(10)
        self.yAxisRange.setMaximum(120)
        self.yAxisRange.setSingleStep(5)
        self.yAxisRange.setProperty("value", 60)
        self.yAxisRange.setObjectName("yAxisRange")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.yAxisRange)
        self.normaliseCheckBox = QtWidgets.QCheckBox(displayControlsDialog)
        self.normaliseCheckBox.setObjectName("normaliseCheckBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.normaliseCheckBox)
        self.normalisationAngleLabel = QtWidgets.QLabel(displayControlsDialog)
        self.normalisationAngleLabel.setObjectName("normalisationAngleLabel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.normalisationAngleLabel)
        self.normalisationAngle = QtWidgets.QComboBox(displayControlsDialog)
        self.normalisationAngle.setObjectName("normalisationAngle")
        self.normalisationAngle.addItem("")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.normalisationAngle)
        self.polarRangeLabel = QtWidgets.QLabel(displayControlsDialog)
        self.polarRangeLabel.setObjectName("polarRangeLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.polarRangeLabel)
        self.polarRange = QtWidgets.QCheckBox(displayControlsDialog)
        self.polarRange.setObjectName("polarRange")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.polarRange)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)

        self.retranslateUi(displayControlsDialog)
        self.buttonBox.accepted.connect(displayControlsDialog.accept)
        self.buttonBox.rejected.connect(displayControlsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(displayControlsDialog)

    def retranslateUi(self, displayControlsDialog):
        _translate = QtCore.QCoreApplication.translate
        displayControlsDialog.setWindowTitle(_translate("displayControlsDialog", "Display"))
        self.colourSchemeLabel.setText(_translate("displayControlsDialog", "Colour Scheme"))
        self.decibelRangeLabel.setText(_translate("displayControlsDialog", "Y Range"))
        self.yAxisRange.setSuffix(_translate("displayControlsDialog", "dB"))
        self.normaliseCheckBox.setText(_translate("displayControlsDialog", "Normalise?"))
        self.normalisationAngleLabel.setText(_translate("displayControlsDialog", "Normalisation Angle"))
        self.normalisationAngle.setItemText(0, _translate("displayControlsDialog", "0"))
        self.polarRangeLabel.setText(_translate("displayControlsDialog", "Polar Range"))
        self.polarRange.setText(_translate("displayControlsDialog", "+/- 180?"))
