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
        self.dataPath = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.dataPath.setObjectName("dataPath")
        self.measurementSelectLayout.addWidget(self.dataPath, 0, 1, 1, 1)
        self.selectDirBtn = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.selectDirBtn.setObjectName("selectDirBtn")
        self.measurementSelectLayout.addWidget(self.selectDirBtn, 0, 0, 1, 1)
        self.measurementView = QtWidgets.QTreeView(self.gridLayoutWidget)
        self.measurementView.setObjectName("measurementView")
        self.measurementSelectLayout.addWidget(self.measurementView, 1, 0, 1, 3)
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
        self.graphLayout.addWidget(self.rightWindowType, 3, 3, 1, 1)
        self.impulseGraph = PlotWidget(self.gridLayoutWidget_2)
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
        self.graphTabs.addTab(self.impulseTab, "")
        self.magnitudeTab = QtWidgets.QWidget()
        self.magnitudeTab.setObjectName("magnitudeTab")
        self.magnitudeGraph = MagnitudeWidget(self.magnitudeTab)
        self.magnitudeGraph.setGeometry(QtCore.QRect(0, 0, 1621, 954))
        self.magnitudeGraph.setObjectName("magnitudeGraph")
        self.graphTabs.addTab(self.magnitudeTab, "")
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
        self.rightWindowSample.valueChanged['int'].connect(MainWindow.updateRightWindowPosition)
        self.zoomButton.clicked.connect(MainWindow.zoomToWindow)
        self.leftWindowSample.valueChanged['int'].connect(MainWindow.updateLeftWindowPosition)
        self.toggleWindowedBtn.clicked.connect(MainWindow.toggleWindowed)
        self.graphTabs.currentChanged['int'].connect(MainWindow.onGraphTabChange)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "pypolarmap"))
        self.selectDirBtn.setText(_translate("MainWindow", "Select Directory"))
        self.label.setText(_translate("MainWindow", "Left Window"))
        self.rightWindowPercent.setSuffix(_translate("MainWindow", "%"))
        self.leftWindowType.setItemText(0, _translate("MainWindow", "Tukey"))
        self.leftWindowType.setItemText(1, _translate("MainWindow", "Hann"))
        self.leftWindowType.setItemText(2, _translate("MainWindow", "Hamming"))
        self.leftWindowType.setItemText(3, _translate("MainWindow", "Blackman-Harris"))
        self.leftWindowType.setItemText(4, _translate("MainWindow", "Nuttall"))
        self.leftWindowPercent.setSuffix(_translate("MainWindow", "%"))
        self.label_2.setText(_translate("MainWindow", "Right Window"))
        self.rightWindowType.setItemText(0, _translate("MainWindow", "Tukey"))
        self.rightWindowType.setItemText(1, _translate("MainWindow", "Hann"))
        self.rightWindowType.setItemText(2, _translate("MainWindow", "Hamming"))
        self.rightWindowType.setItemText(3, _translate("MainWindow", "Blackman-Harris"))
        self.rightWindowType.setItemText(4, _translate("MainWindow", "Nuttall"))
        self.toggleWindowedBtn.setText(_translate("MainWindow", "Show Windowed IR"))
        self.zoomButton.setText(_translate("MainWindow", "Zoom"))
        self.graphTabs.setTabText(self.graphTabs.indexOf(self.impulseTab), _translate("MainWindow", "Impulse"))
        self.graphTabs.setTabText(self.graphTabs.indexOf(self.magnitudeTab), _translate("MainWindow", "Magnitude"))

from model.magnitude import MagnitudeWidget
from pyqtgraph import PlotWidget
