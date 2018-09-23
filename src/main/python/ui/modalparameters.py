# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'modalparameters.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_modalParametersDialog(object):
    def setupUi(self, modalParametersDialog):
        modalParametersDialog.setObjectName("modalParametersDialog")
        modalParametersDialog.resize(338, 380)
        self.gridLayout = QtWidgets.QGridLayout(modalParametersDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_5 = QtWidgets.QLabel(modalParametersDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.label_5.setWordWrap(True)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.measurementDistance = QtWidgets.QDoubleSpinBox(modalParametersDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.measurementDistance.sizePolicy().hasHeightForWidth())
        self.measurementDistance.setSizePolicy(sizePolicy)
        self.measurementDistance.setMinimum(0.1)
        self.measurementDistance.setMaximum(10.0)
        self.measurementDistance.setSingleStep(0.01)
        self.measurementDistance.setProperty("value", 1.0)
        self.measurementDistance.setObjectName("measurementDistance")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.measurementDistance)
        self.label_12 = QtWidgets.QLabel(modalParametersDialog)
        self.label_12.setObjectName("label_12")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_12)
        self.boxRadius = QtWidgets.QDoubleSpinBox(modalParametersDialog)
        self.boxRadius.setMinimum(0.01)
        self.boxRadius.setMaximum(3.0)
        self.boxRadius.setSingleStep(0.01)
        self.boxRadius.setProperty("value", 0.25)
        self.boxRadius.setObjectName("boxRadius")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.boxRadius)
        self.label_6 = QtWidgets.QLabel(modalParametersDialog)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.driverRadius = QtWidgets.QDoubleSpinBox(modalParametersDialog)
        self.driverRadius.setDecimals(1)
        self.driverRadius.setMinimum(1.0)
        self.driverRadius.setMaximum(40.0)
        self.driverRadius.setSingleStep(0.1)
        self.driverRadius.setProperty("value", 15.0)
        self.driverRadius.setObjectName("driverRadius")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.driverRadius)
        self.label_7 = QtWidgets.QLabel(modalParametersDialog)
        self.label_7.setWordWrap(False)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.modalCoeffs = QtWidgets.QSpinBox(modalParametersDialog)
        self.modalCoeffs.setMinimum(5)
        self.modalCoeffs.setMaximum(14)
        self.modalCoeffs.setProperty("value", 14)
        self.modalCoeffs.setObjectName("modalCoeffs")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.modalCoeffs)
        self.label_8 = QtWidgets.QLabel(modalParametersDialog)
        self.label_8.setObjectName("label_8")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_8)
        self.f0 = QtWidgets.QSpinBox(modalParametersDialog)
        self.f0.setMinimum(1)
        self.f0.setMaximum(200)
        self.f0.setProperty("value", 70)
        self.f0.setObjectName("f0")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.f0)
        self.label_9 = QtWidgets.QLabel(modalParametersDialog)
        self.label_9.setObjectName("label_9")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label_9)
        self.q0 = QtWidgets.QDoubleSpinBox(modalParametersDialog)
        self.q0.setDecimals(3)
        self.q0.setMinimum(0.2)
        self.q0.setMaximum(1.5)
        self.q0.setSingleStep(0.001)
        self.q0.setProperty("value", 0.7)
        self.q0.setObjectName("q0")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.q0)
        self.label_10 = QtWidgets.QLabel(modalParametersDialog)
        self.label_10.setWordWrap(True)
        self.label_10.setObjectName("label_10")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_10)
        self.transFreq = QtWidgets.QSpinBox(modalParametersDialog)
        self.transFreq.setMinimum(1)
        self.transFreq.setMaximum(1000)
        self.transFreq.setProperty("value", 200)
        self.transFreq.setObjectName("transFreq")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.transFreq)
        self.label_11 = QtWidgets.QLabel(modalParametersDialog)
        self.label_11.setObjectName("label_11")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.label_11)
        self.lfGain = QtWidgets.QDoubleSpinBox(modalParametersDialog)
        self.lfGain.setDecimals(1)
        self.lfGain.setMinimum(-10.0)
        self.lfGain.setMaximum(10.0)
        self.lfGain.setSingleStep(0.1)
        self.lfGain.setObjectName("lfGain")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.lfGain)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(modalParametersDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(modalParametersDialog)
        self.buttonBox.accepted.connect(modalParametersDialog.accept)
        self.buttonBox.rejected.connect(modalParametersDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(modalParametersDialog)

    def retranslateUi(self, modalParametersDialog):
        _translate = QtCore.QCoreApplication.translate
        modalParametersDialog.setWindowTitle(_translate("modalParametersDialog", "Modal Parameters"))
        self.label_5.setText(_translate("modalParametersDialog", "Measurement Distance (m)"))
        self.label_12.setText(_translate("modalParametersDialog", "Box Radius (m)"))
        self.label_6.setText(_translate("modalParametersDialog", "Driver Radius (cm)"))
        self.label_7.setText(_translate("modalParametersDialog", "Modal Coefficients"))
        self.label_8.setText(_translate("modalParametersDialog", "f0"))
        self.label_9.setText(_translate("modalParametersDialog", "q0"))
        self.label_10.setText(_translate("modalParametersDialog", "Transition Frequency (Hz)"))
        self.label_11.setText(_translate("modalParametersDialog", "LF Gain (dB)"))
