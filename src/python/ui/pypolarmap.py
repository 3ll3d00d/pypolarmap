# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pypolarmap.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(2229, 1162)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 581, 1091))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.measurementSelectLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.measurementSelectLayout.setContentsMargins(0, 0, 0, 0)
        self.measurementSelectLayout.setObjectName("measurementSelectLayout")
        self.label_5 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_5.setObjectName("label_5")
        self.measurementSelectLayout.addWidget(self.label_5, 3, 0, 1, 1)
        self.measurementDistance = QtWidgets.QDoubleSpinBox(self.gridLayoutWidget)
        self.measurementDistance.setMinimum(0.1)
        self.measurementDistance.setMaximum(10.0)
        self.measurementDistance.setSingleStep(0.01)
        self.measurementDistance.setProperty("value", 1.0)
        self.measurementDistance.setObjectName("measurementDistance")
        self.measurementSelectLayout.addWidget(self.measurementDistance, 3, 1, 1, 1)
        self.driverRadius = QtWidgets.QDoubleSpinBox(self.gridLayoutWidget)
        self.driverRadius.setDecimals(1)
        self.driverRadius.setMinimum(1.0)
        self.driverRadius.setMaximum(40.0)
        self.driverRadius.setSingleStep(0.1)
        self.driverRadius.setProperty("value", 15.0)
        self.driverRadius.setObjectName("driverRadius")
        self.measurementSelectLayout.addWidget(self.driverRadius, 5, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_6.setObjectName("label_6")
        self.measurementSelectLayout.addWidget(self.label_6, 5, 0, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_13.setObjectName("label_13")
        self.measurementSelectLayout.addWidget(self.label_13, 2, 0, 1, 1)
        self.transFreq = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.transFreq.setMinimum(1)
        self.transFreq.setMaximum(1000)
        self.transFreq.setProperty("value", 200)
        self.transFreq.setObjectName("transFreq")
        self.measurementSelectLayout.addWidget(self.transFreq, 9, 1, 1, 1)
        self.label_11 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_11.setObjectName("label_11")
        self.measurementSelectLayout.addWidget(self.label_11, 10, 0, 1, 1)
        self.lfGain = QtWidgets.QDoubleSpinBox(self.gridLayoutWidget)
        self.lfGain.setDecimals(1)
        self.lfGain.setMinimum(-10.0)
        self.lfGain.setMaximum(10.0)
        self.lfGain.setSingleStep(0.1)
        self.lfGain.setObjectName("lfGain")
        self.measurementSelectLayout.addWidget(self.lfGain, 10, 1, 1, 1)
        self.measurementView = QtWidgets.QTreeView(self.gridLayoutWidget)
        self.measurementView.setObjectName("measurementView")
        self.measurementSelectLayout.addWidget(self.measurementView, 1, 0, 1, 3)
        self.label_8 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_8.setObjectName("label_8")
        self.measurementSelectLayout.addWidget(self.label_8, 7, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_7.setObjectName("label_7")
        self.measurementSelectLayout.addWidget(self.label_7, 6, 0, 1, 1)
        self.modalCoeffs = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.modalCoeffs.setMinimum(5)
        self.modalCoeffs.setMaximum(14)
        self.modalCoeffs.setProperty("value", 14)
        self.modalCoeffs.setObjectName("modalCoeffs")
        self.measurementSelectLayout.addWidget(self.modalCoeffs, 6, 1, 1, 1)
        self.f0 = QtWidgets.QSpinBox(self.gridLayoutWidget)
        self.f0.setMinimum(1)
        self.f0.setMaximum(200)
        self.f0.setProperty("value", 70)
        self.f0.setObjectName("f0")
        self.measurementSelectLayout.addWidget(self.f0, 7, 1, 1, 1)
        self.q0 = QtWidgets.QDoubleSpinBox(self.gridLayoutWidget)
        self.q0.setDecimals(3)
        self.q0.setMinimum(0.2)
        self.q0.setMaximum(1.5)
        self.q0.setSingleStep(0.001)
        self.q0.setProperty("value", 0.7)
        self.q0.setObjectName("q0")
        self.measurementSelectLayout.addWidget(self.q0, 8, 1, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_9.setObjectName("label_9")
        self.measurementSelectLayout.addWidget(self.label_9, 8, 0, 1, 1)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.measurementSelectLayout.addLayout(self.formLayout, 11, 0, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_10.setObjectName("label_10")
        self.measurementSelectLayout.addWidget(self.label_10, 9, 0, 1, 1)
        self.boxRadius = QtWidgets.QDoubleSpinBox(self.gridLayoutWidget)
        self.boxRadius.setMinimum(0.01)
        self.boxRadius.setMaximum(3.0)
        self.boxRadius.setSingleStep(0.01)
        self.boxRadius.setProperty("value", 0.25)
        self.boxRadius.setObjectName("boxRadius")
        self.measurementSelectLayout.addWidget(self.boxRadius, 4, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_12.setObjectName("label_12")
        self.measurementSelectLayout.addWidget(self.label_12, 4, 0, 1, 1)
        self.selectDirBtn = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.selectDirBtn.setObjectName("selectDirBtn")
        self.measurementSelectLayout.addWidget(self.selectDirBtn, 0, 0, 1, 1)
        self.dataPath = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.dataPath.setObjectName("dataPath")
        self.measurementSelectLayout.addWidget(self.dataPath, 0, 1, 1, 1)
        self.fs = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.fs.setEnabled(False)
        self.fs.setObjectName("fs")
        self.fs.addItem("")
        self.fs.addItem("")
        self.fs.addItem("")
        self.measurementSelectLayout.addWidget(self.fs, 2, 1, 1, 1)
        self.graphTabs = QtWidgets.QTabWidget(self.centralwidget)
        self.graphTabs.setGeometry(QtCore.QRect(600, 10, 1631, 1091))
        self.graphTabs.setObjectName("graphTabs")
        self.impulseTab = QtWidgets.QWidget()
        self.impulseTab.setObjectName("impulseTab")
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.impulseTab)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(0, 0, 1621, 1061))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.graphLayout = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.graphLayout.setContentsMargins(0, 0, 0, 0)
        self.graphLayout.setObjectName("graphLayout")
        self.leftWindowSample = QtWidgets.QSpinBox(self.gridLayoutWidget_2)
        self.leftWindowSample.setObjectName("leftWindowSample")
        self.graphLayout.addWidget(self.leftWindowSample, 3, 2, 1, 1)
        self.label = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.graphLayout.addWidget(self.label, 2, 0, 1, 3)
        self.rightWindowPercent = QtWidgets.QSpinBox(self.gridLayoutWidget_2)
        self.rightWindowPercent.setMinimum(12)
        self.rightWindowPercent.setMaximum(75)
        self.rightWindowPercent.setProperty("value", 50)
        self.rightWindowPercent.setObjectName("rightWindowPercent")
        self.graphLayout.addWidget(self.rightWindowPercent, 3, 4, 1, 1)
        self.rightWindowSample = QtWidgets.QSpinBox(self.gridLayoutWidget_2)
        self.rightWindowSample.setObjectName("rightWindowSample")
        self.graphLayout.addWidget(self.rightWindowSample, 3, 5, 1, 1)
        self.leftWindowType = QtWidgets.QComboBox(self.gridLayoutWidget_2)
        self.leftWindowType.setObjectName("leftWindowType")
        self.leftWindowType.addItem("")
        self.leftWindowType.addItem("")
        self.leftWindowType.addItem("")
        self.leftWindowType.addItem("")
        self.leftWindowType.addItem("")
        self.leftWindowType.addItem("")
        self.graphLayout.addWidget(self.leftWindowType, 3, 0, 1, 1)
        self.leftWindowPercent = QtWidgets.QSpinBox(self.gridLayoutWidget_2)
        self.leftWindowPercent.setMinimum(12)
        self.leftWindowPercent.setMaximum(75)
        self.leftWindowPercent.setProperty("value", 50)
        self.leftWindowPercent.setObjectName("leftWindowPercent")
        self.graphLayout.addWidget(self.leftWindowPercent, 3, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.graphLayout.addWidget(self.label_2, 2, 3, 1, 3)
        self.rightWindowType = QtWidgets.QComboBox(self.gridLayoutWidget_2)
        self.rightWindowType.setObjectName("rightWindowType")
        self.rightWindowType.addItem("")
        self.rightWindowType.addItem("")
        self.rightWindowType.addItem("")
        self.rightWindowType.addItem("")
        self.rightWindowType.addItem("")
        self.rightWindowType.addItem("")
        self.graphLayout.addWidget(self.rightWindowType, 3, 3, 1, 1)
        self.impulseGraph = MplWidget(self.gridLayoutWidget_2)
        self.impulseGraph.setObjectName("impulseGraph")
        self.graphLayout.addWidget(self.impulseGraph, 0, 0, 1, 6)
        self.toggleWindowedBtn = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.toggleWindowedBtn.setEnabled(False)
        self.toggleWindowedBtn.setCheckable(True)
        self.toggleWindowedBtn.setFlat(False)
        self.toggleWindowedBtn.setObjectName("toggleWindowedBtn")
        self.graphLayout.addWidget(self.toggleWindowedBtn, 1, 0, 1, 1)
        self.zoomButton = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.zoomButton.setEnabled(False)
        self.zoomButton.setObjectName("zoomButton")
        self.graphLayout.addWidget(self.zoomButton, 1, 1, 1, 1)
        self.pushButton = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.pushButton.setObjectName("pushButton")
        self.graphLayout.addWidget(self.pushButton, 1, 2, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(self.gridLayoutWidget_2)
        self.pushButton_2.setObjectName("pushButton_2")
        self.graphLayout.addWidget(self.pushButton_2, 1, 3, 1, 1)
        self.graphTabs.addTab(self.impulseTab, "")
        self.magnitudeTab = QtWidgets.QWidget()
        self.magnitudeTab.setObjectName("magnitudeTab")
        self.magnitudeGraph = MplWidget(self.magnitudeTab)
        self.magnitudeGraph.setGeometry(QtCore.QRect(0, 0, 1621, 954))
        self.magnitudeGraph.setObjectName("magnitudeGraph")
        self.graphTabs.addTab(self.magnitudeTab, "")
        self.polarTab = QtWidgets.QWidget()
        self.polarTab.setObjectName("polarTab")
        self.polarGraph = MplWidget(self.polarTab)
        self.polarGraph.setGeometry(QtCore.QRect(0, 0, 1621, 954))
        self.polarGraph.setObjectName("polarGraph")
        self.gridLayoutWidget_3 = QtWidgets.QWidget(self.polarTab)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(-1, 960, 531, 61))
        self.gridLayoutWidget_3.setObjectName("gridLayoutWidget_3")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.colourMapSelector = QtWidgets.QComboBox(self.gridLayoutWidget_3)
        self.colourMapSelector.setObjectName("colourMapSelector")
        self.gridLayout.addWidget(self.colourMapSelector, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.gridLayoutWidget_3)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.contourInterval = QtWidgets.QSpinBox(self.gridLayoutWidget_3)
        self.contourInterval.setMinimum(1)
        self.contourInterval.setMaximum(12)
        self.contourInterval.setProperty("value", 3)
        self.contourInterval.setObjectName("contourInterval")
        self.gridLayout.addWidget(self.contourInterval, 1, 1, 1, 1)
        self.graphTabs.addTab(self.polarTab, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.modalGraph = MplWidget(self.tab)
        self.modalGraph.setGeometry(QtCore.QRect(0, 0, 1621, 954))
        self.modalGraph.setObjectName("modalGraph")
        self.gridLayoutWidget_4 = QtWidgets.QWidget(self.tab)
        self.gridLayoutWidget_4.setGeometry(QtCore.QRect(-1, 959, 131, 91))
        self.gridLayoutWidget_4.setObjectName("gridLayoutWidget_4")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget_4)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.refreshSpatialBtn = QtWidgets.QPushButton(self.gridLayoutWidget_4)
        self.refreshSpatialBtn.setObjectName("refreshSpatialBtn")
        self.gridLayout_2.addWidget(self.refreshSpatialBtn, 0, 0, 1, 1)
        self.graphTabs.addTab(self.tab, "")
        self.graphTabs.raise_()
        self.gridLayoutWidget.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 2229, 31))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.graphTabs.setCurrentIndex(0)
        self.selectDirBtn.clicked.connect(MainWindow.selectDirectory)
        self.rightWindowSample.editingFinished.connect(MainWindow.updateRightWindowPosition)
        self.zoomButton.clicked.connect(MainWindow.zoomIn)
        self.leftWindowSample.editingFinished.connect(MainWindow.updateLeftWindowPosition)
        self.toggleWindowedBtn.clicked.connect(MainWindow.toggleWindowed)
        self.graphTabs.currentChanged['int'].connect(MainWindow.onGraphTabChange)
        self.pushButton.clicked.connect(MainWindow.zoomOut)
        self.pushButton_2.clicked.connect(MainWindow.updateWindow)
        self.colourMapSelector.currentIndexChanged['QString'].connect(MainWindow.updateColourMap)
        self.contourInterval.valueChanged['int'].connect(MainWindow.updateContourInterval)
        self.measurementDistance.valueChanged['double'].connect(MainWindow.updateMeasurementDistance)
        self.driverRadius.valueChanged['double'].connect(MainWindow.updateDriverRadius)
        self.modalCoeffs.valueChanged['int'].connect(MainWindow.updateModalCoeffs)
        self.f0.valueChanged['int'].connect(MainWindow.updateF0)
        self.q0.valueChanged['double'].connect(MainWindow.updateQ0)
        self.transFreq.valueChanged['int'].connect(MainWindow.updateTransitionFrequency)
        self.lfGain.valueChanged['double'].connect(MainWindow.updateLFGain)
        self.boxRadius.valueChanged['double'].connect(MainWindow.updateBoxRadius)
        self.refreshSpatialBtn.clicked.connect(MainWindow.refreshModal)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "pypolarmap"))
        self.label_5.setText(_translate("MainWindow", "Measurement Distance (m)"))
        self.label_6.setText(_translate("MainWindow", "Driver Radius (cm)"))
        self.label_13.setText(_translate("MainWindow", "Fs"))
        self.label_11.setText(_translate("MainWindow", "LF Gain (dB)"))
        self.label_8.setText(_translate("MainWindow", "f0"))
        self.label_7.setText(_translate("MainWindow", "Modal Coefficients"))
        self.label_9.setText(_translate("MainWindow", "q0"))
        self.label_10.setText(_translate("MainWindow", "Transition Frequency (Hz)"))
        self.label_12.setText(_translate("MainWindow", "Box Radius (m)"))
        self.selectDirBtn.setText(_translate("MainWindow", "Load Measurements"))
        self.fs.setCurrentText(_translate("MainWindow", "48000"))
        self.fs.setItemText(0, _translate("MainWindow", "44100"))
        self.fs.setItemText(1, _translate("MainWindow", "48000"))
        self.fs.setItemText(2, _translate("MainWindow", "96000"))
        self.label.setText(_translate("MainWindow", "Left Window"))
        self.rightWindowPercent.setSuffix(_translate("MainWindow", "%"))
        self.leftWindowType.setItemText(0, _translate("MainWindow", "Rectangle"))
        self.leftWindowType.setItemText(1, _translate("MainWindow", "Tukey"))
        self.leftWindowType.setItemText(2, _translate("MainWindow", "Hann"))
        self.leftWindowType.setItemText(3, _translate("MainWindow", "Hamming"))
        self.leftWindowType.setItemText(4, _translate("MainWindow", "Blackman-Harris"))
        self.leftWindowType.setItemText(5, _translate("MainWindow", "Nuttall"))
        self.leftWindowPercent.setSuffix(_translate("MainWindow", "%"))
        self.label_2.setText(_translate("MainWindow", "Right Window"))
        self.rightWindowType.setItemText(0, _translate("MainWindow", "Rectangle"))
        self.rightWindowType.setItemText(1, _translate("MainWindow", "Tukey"))
        self.rightWindowType.setItemText(2, _translate("MainWindow", "Hann"))
        self.rightWindowType.setItemText(3, _translate("MainWindow", "Hamming"))
        self.rightWindowType.setItemText(4, _translate("MainWindow", "Blackman-Harris"))
        self.rightWindowType.setItemText(5, _translate("MainWindow", "Nuttall"))
        self.toggleWindowedBtn.setText(_translate("MainWindow", "Show Windowed IR"))
        self.zoomButton.setText(_translate("MainWindow", "Zoom In"))
        self.pushButton.setText(_translate("MainWindow", "Zoom Out"))
        self.pushButton_2.setText(_translate("MainWindow", "Apply Window"))
        self.graphTabs.setTabText(self.graphTabs.indexOf(self.impulseTab), _translate("MainWindow", "Impulse"))
        self.graphTabs.setTabText(self.graphTabs.indexOf(self.magnitudeTab), _translate("MainWindow", "Magnitude"))
        self.label_3.setText(_translate("MainWindow", "Colour Map"))
        self.label_4.setText(_translate("MainWindow", "Contour Interval (dB)"))
        self.graphTabs.setTabText(self.graphTabs.indexOf(self.polarTab), _translate("MainWindow", "Polar"))
        self.refreshSpatialBtn.setText(_translate("MainWindow", "Refresh"))
        self.graphTabs.setTabText(self.graphTabs.indexOf(self.tab), _translate("MainWindow", "Modal"))

from app import MplWidget
