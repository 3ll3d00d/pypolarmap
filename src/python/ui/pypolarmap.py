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
        MainWindow.resize(1645, 1022)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 581, 451))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.measurementSelectLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.measurementSelectLayout.setContentsMargins(0, 0, 0, 0)
        self.measurementSelectLayout.setObjectName("measurementSelectLayout")
        self.dataPathLabel = QtWidgets.QLabel(self.gridLayoutWidget)
        self.dataPathLabel.setObjectName("dataPathLabel")
        self.measurementSelectLayout.addWidget(self.dataPathLabel, 0, 0, 1, 3)
        self.selectDirBtn = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.selectDirBtn.setObjectName("selectDirBtn")
        self.measurementSelectLayout.addWidget(self.selectDirBtn, 1, 0, 1, 1)
        self.dataPath = QtWidgets.QLineEdit(self.gridLayoutWidget)
        self.dataPath.setObjectName("dataPath")
        self.measurementSelectLayout.addWidget(self.dataPath, 1, 1, 1, 1)
        self.measurementView = QtWidgets.QTreeView(self.gridLayoutWidget)
        self.measurementView.setObjectName("measurementView")
        self.measurementSelectLayout.addWidget(self.measurementView, 2, 1, 1, 2)
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(600, 10, 1021, 861))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.graphLayout = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.graphLayout.setContentsMargins(0, 0, 0, 0)
        self.graphLayout.setObjectName("graphLayout")
        self.leftWindowSample = QtWidgets.QSpinBox(self.gridLayoutWidget_2)
        self.leftWindowSample.setObjectName("leftWindowSample")
        self.graphLayout.addWidget(self.leftWindowSample, 2, 1, 1, 1)
        self.rightWindowSample = QtWidgets.QSpinBox(self.gridLayoutWidget_2)
        self.rightWindowSample.setObjectName("rightWindowSample")
        self.graphLayout.addWidget(self.rightWindowSample, 2, 3, 1, 1)
        self.mainGraph = PlotWidget(self.gridLayoutWidget_2)
        self.mainGraph.setObjectName("mainGraph")
        self.graphLayout.addWidget(self.mainGraph, 0, 0, 1, 4)
        self.leftWindowType = QtWidgets.QComboBox(self.gridLayoutWidget_2)
        self.leftWindowType.setObjectName("leftWindowType")
        self.graphLayout.addWidget(self.leftWindowType, 2, 0, 1, 1)
        self.rightWindowType = QtWidgets.QComboBox(self.gridLayoutWidget_2)
        self.rightWindowType.setObjectName("rightWindowType")
        self.graphLayout.addWidget(self.rightWindowType, 2, 2, 1, 1)
        self.label = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.graphLayout.addWidget(self.label, 1, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget_2)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.graphLayout.addWidget(self.label_2, 1, 2, 1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1645, 31))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.selectDirBtn.clicked.connect(MainWindow.selectDirectory)
        self.leftWindowSample.valueChanged['int'].connect(MainWindow.updateLeftWindowPosition)
        self.leftWindowType.currentIndexChanged['int'].connect(MainWindow.updateLeftWindowType)
        self.rightWindowType.currentIndexChanged['int'].connect(MainWindow.updateRightWindowType)
        self.rightWindowSample.valueChanged['int'].connect(MainWindow.updateRightWindowPosition)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "pypolarmap"))
        self.dataPathLabel.setText(_translate("MainWindow", "Enter the path to the measurements"))
        self.selectDirBtn.setText(_translate("MainWindow", "Select Directory"))
        self.label.setText(_translate("MainWindow", "Left Window"))
        self.label_2.setText(_translate("MainWindow", "Right Window"))

from pyqtgraph import PlotWidget
