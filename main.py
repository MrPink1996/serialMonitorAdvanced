from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QDialog, QProgressBar, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QLayout, QComboBox, QTextBrowser, QCheckBox, QLineEdit, QMessageBox
import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
import time
import glob
import serial
import pyqtgraph as pg
import os, sys
import numpy as np

# global variables
class serialMonitor(QThread):
    trigger_monitor = pyqtSignal()
    trigger_plot = pyqtSignal()
    y = []
    text = ""
    ser = serial.Serial()
    nGraphs = 1
    controll = True
    plotting = False
    splitPlots = False
    def setConfiguration(self, conf):
        self.ser.port  = conf[0]
        self.ser.baudrate = conf[1]
        if(conf[3] == "none"):
            self.ser.parity = serial.PARITY_NONE
        if(conf[2] == 8):
            self.ser.bytesize = serial.EIGHTBITS
        if(conf[4] == 1):
            self.ser.stopbits = serial.STOPBITS_ONE

    def stop(self):
        self.controll = False

    def run(self):
        self.ser.open()
        self.ser.setDTR(False)
        self.ser.setDTR(True)

        while(self.controll):
            try:
                self.text = self.ser.readline()
                if(self.controll == False):
                    break
                self.text = self.text.decode()
                if(self.text.find(',') != -1 ):
                    self.nGraphs = len(self.text.split(","))
                if(self.plotting):
                    if(self.nGraphs > 1):
                        buffer = self.text.split(",")
                        self.nGraphs = len(buffer)
                        self.y = [float(item) for item in buffer]
                    else:
                        self.y = float(self.text)
                    self.trigger_plot.emit()
                self.trigger_monitor.emit()
            except Exception as e:
                print("Unexpected error:", e)
        self.ser.close() 
        self.exit()

class Window(QDialog):
    serialPorts = glob.glob('/dev/tty*')
    connectButtonState = False
    plottingButtonState = False
    nValues = 100


    textBrowserText = ""
    nGraphs = 1
    y = np.zeros((nGraphs, nValues))
    #y = np.zeros(100)
    x = np.arange(start=0, stop=nValues, step=1)
    pen = []
    pen.append(pg.mkPen(color=(0, 0, 0), width=5))
    #monitor_text = []

    def setupLayout(self):
        # MAIN PAGE LAYOUT
        self.mainPage_vertical = QVBoxLayout()
        self.mainPage_vertical.setContentsMargins(0, 0, 0, 0)
        self.mainPage_vertical.setObjectName("mainPage_vertical")
        self.sidePage_horizontal = QHBoxLayout()
        self.sidePage_horizontal.setObjectName("sidePage_horizontal")

        # MAIN MENU LEFT
        self.layout_monitor = QVBoxLayout()
        self.layout_monitor.setObjectName("layout_monitor")
        self.connectionBar = QHBoxLayout()
        self.connectionBar.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.connectionBar.setSpacing(0)
        self.connectionBar.setObjectName("connectionBar")
        # SETTINGS LEFT
        self.settings_monitor = QVBoxLayout()
        self.settings_monitor.setSizeConstraint(QLayout.SetFixedSize)
        self.settings_monitor.setSpacing(0)
        self.settings_monitor.setObjectName("settings_monitor")
        # BAUDRATE LEFT
        self.baudrateMenu = QComboBox()
        self.baudrateMenu.setObjectName("baudrateMenu")
        self.baudrateMenu.addItem("")
        self.baudrateMenu.addItem("")
        self.baudrateMenu.addItem("")
        self.baudrateMenu.setItemText(0, "9600")
        self.baudrateMenu.setItemText(1, "38400")
        self.baudrateMenu.setItemText(2, "115200")
        self.baudrateMenu.setCurrentIndex(2)
        # DATABITS LEFT
        self.dataBitsMenu = QComboBox()
        self.dataBitsMenu.setObjectName("dataBitsMenu")
        self.dataBitsMenu.addItem("")
        self.dataBitsMenu.addItem("")
        self.dataBitsMenu.addItem("")
        self.dataBitsMenu.addItem("") 
        self.dataBitsMenu.setItemText(0, "5")
        self.dataBitsMenu.setItemText(1, "6")
        self.dataBitsMenu.setItemText(2, "7")
        self.dataBitsMenu.setItemText(3, "8")
        self.dataBitsMenu.setCurrentIndex(3)

        # PARITY LEFT
        self.paritiyMenu = QComboBox()
        self.paritiyMenu.setObjectName("paritiyMenu")
        self.paritiyMenu.addItem("")
        self.paritiyMenu.addItem("")
        self.paritiyMenu.addItem("") 
        self.paritiyMenu.setItemText(0, "none")
        self.paritiyMenu.setItemText(1, "odd")
        self.paritiyMenu.setItemText(2, "even")
        self.paritiyMenu.setCurrentIndex(0)
        # STOPBITS LEFT
        self.stopBitsMenu = QComboBox()
        self.stopBitsMenu.setObjectName("stopBitsMenu")
        self.stopBitsMenu.addItem("")
        self.stopBitsMenu.addItem("")
        self.stopBitsMenu.addItem("")
        self.stopBitsMenu.setItemText(0, "1")
        self.stopBitsMenu.setItemText(1, "1.5")
        self.stopBitsMenu.setItemText(2, "2")
        self.stopBitsMenu.setCurrentIndex(0)
        # PORTS LEFT
        self.portMenu = QComboBox()
        self.portMenu.setObjectName("portMenu")
        for i in range(len(self.serialPorts)):
            self.portMenu.addItem("")
            self.portMenu.setItemText(i, str(self.serialPorts[i]))
        self.portMenu.setCurrentIndex(0)
        # TIMESTAMPS LEFt
        self.timeStampCheckBox = QCheckBox()
        self.timeStampCheckBox.setMaximumSize(QSize(1678238, 16777215))
        self.timeStampCheckBox.setBaseSize(QSize(0, 0))
        self.timeStampCheckBox.setObjectName("timeStampCheckBox")
        self.timeStampCheckBox.setText("Show Timestamp")
        # CONNECTION BAR LEFT
        self.connectionBar.addLayout(self.settings_monitor)
        self.connectionButton= QPushButton()
        self.connectionButton.setMaximumSize(QSize(16777215, 170))
        self.connectionButton.setObjectName("connectionButton")
        self.connectionButton.setText("Connect")
        # TEXTBROWSER LEFT
        self.textBrowser = QTextBrowser()
        self.textBrowser.setObjectName("textBrowser")
        # SEND BAR LEFT
        self.sendBar = QHBoxLayout()
        self.sendBar.setObjectName("sendBar")
        self.sendLine = QLineEdit()
        self.sendLine.setObjectName("sendLine")
        self.sendButton = QPushButton()
        self.sendButton.setObjectName("sendButton")
        self.sendButton.setText("Send")
        # UPDATE LAYOUT LEFT
        self.connectionBar.addWidget(self.connectionButton)
        self.sendBar.addWidget(self.sendButton)
        self.layout_monitor.addLayout(self.connectionBar)
        self.layout_monitor.addWidget(self.textBrowser)
        self.sendBar.addWidget(self.sendLine)
        self.layout_monitor.addLayout(self.sendBar)
        self.sidePage_horizontal.addLayout(self.layout_monitor)
        self.settings_monitor.addWidget(self.portMenu)
        self.settings_monitor.addWidget(self.baudrateMenu)
        self.settings_monitor.addWidget(self.dataBitsMenu)
        self.settings_monitor.addWidget(self.paritiyMenu)
        self.settings_monitor.addWidget(self.stopBitsMenu)
        self.settings_monitor.addWidget(self.timeStampCheckBox)

        # MAIN MENU RIGHT
        self.layout_right = QVBoxLayout()
        self.layout_right.setObjectName("layout_right")
        self.plotBar = QHBoxLayout()
        self.plotBar.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.plotBar.setSpacing(0)
        self.plotBar.setObjectName("plotBar")
        # CONNECTION BAR RIGHT
        self.plotButton = QPushButton()
        self.plotButton.setMaximumSize(QSize(16777215, 170))
        self.plotButton.setObjectName("plotButton")
        self.plotButton.setText("Enable Plotting")
        
        # SPLIT PLOTS
        self.splitPlotsCheckBox = QCheckBox()
        self.splitPlotsCheckBox.setMaximumSize(QSize(1678238, 16777215))
        self.splitPlotsCheckBox.setBaseSize(QSize(0, 0))
        self.splitPlotsCheckBox.setObjectName("splitPlotsCheckBox")
        self.splitPlotsCheckBox.setText("Split Plots")

        # TEXTBROWSER RIGHT
        self.graph = []
        self.graph.append(pg.PlotWidget())
        self.graph[0].setObjectName("graph")
        self.graph[0].setBackground('w')
        # UPDATE LAYOUT RIGHT
        self.plotBar.addWidget(self.plotButton)
        self.plotBar.addWidget(self.splitPlotsCheckBox)
        self.layout_right.addLayout(self.plotBar)
        self.layout_right.addWidget(self.graph[0])

        # UPDATE MAIN LAYOUT
        self.sidePage_horizontal.addLayout(self.layout_right)
        self.mainPage_vertical.addLayout(self.sidePage_horizontal)
        self.setLayout(self.mainPage_vertical)

    def setupLayout2(self):
        if(self.splitPlotsCheckBox.isChecked()):
            self.layout_right.removeWidget(self.graph[0])
            self.graph = []
            for i in range(self.nGraphs):
                self.graph.append(pg.PlotWidget())
                self.graph[i].setObjectName("graph" + str(i))
                self.graph[i].setBackground('w')
                self.layout_right.addWidget(self.graph[i])
        else:
            for i in range(len(self.graph)):
                self.layout_right.removeWidget(self.graph[i])
            self.graph = []
            self.graph.append(pg.PlotWidget())
            self.graph[0].setObjectName("graph0")
            self.graph[0].setBackground('w')
            self.layout_right.addWidget(self.graph[0])


    def __init__(self):
        super().__init__()
        self.resize(995, 641)
        self.setupLayout()
        
        # CALLBACKS        
        self.connectionButton.clicked.connect(self.onPressedConnectButton)
        self.plotButton.clicked.connect(self.onPressedPlotButton)
        self.splitPlotsCheckBox.clicked.connect(self.onPressedSplitPlots)
        #self.sendButton_left.clicked.connect(self.onPressedSendButtonLeft)
        self.show()

    def onPressedSplitPlots(self):
        self.graphData = []
        if(self.splitPlotsCheckBox.isChecked() == False):
            for i in range(len(self.y)):
                buffer = self.graph[0].plot(self.x, self.y[i], pen=self.pen[i], symbol='o', symbolSize=3, symbolBrush='k')
                self.graphData.append(buffer)
        else:
            for i in range(len(self.y)):
                buffer = self.graph[i].plot(self.x, self.y[i], pen=self.pen[i], symbol='o', symbolSize=3, symbolBrush='k')
                self.graphData.append(buffer)
        self.setupLayout2()
        self.splitPlots = True

    def onPressedConnectButton(self):
        if(self.connectButtonState == False):
            self.thread = serialMonitor()
            self.thread.setConfiguration([str(self.portMenu.currentText()), int(self.baudrateMenu.currentText()), int(self.dataBitsMenu.currentText()), str(self.paritiyMenu.currentText()), int(self.stopBitsMenu.currentText())])
            self.thread.trigger_monitor.connect(self.updateMonitor)
            self.thread.trigger_plot.connect(self.updatePlot)        
            self.thread.start()
            self.connectButtonState = True
            self.connectionButton.setText("Disconnect")
            self.connectionButton.repaint()
        else:
            self.connectButtonState = False
            self.thread.stop()
            self.connectionButton.setText("Connect")
            self.connectionButton.repaint()


    def onPressedPlotButton(self):
        if(self.plottingButtonState == False):
            self.pen = []
            for i in range(self.nGraphs):
                self.pen.append(pg.mkPen(color=(min(255*i, 255), (1 - np.mod(i, 2))*150, 100*i), width=5))
            self.y = np.zeros((self.nGraphs, self.nValues))
            self.graphData = []
            if(self.splitPlotsCheckBox.isChecked() == False):
                for i in range(len(self.y)):
                    buffer = self.graph[0].plot(self.x, self.y[i], pen=self.pen[i], symbol='o', symbolSize=3, symbolBrush='k')
                    self.graphData.append(buffer)
            else:
                for i in range(len(self.y)):
                    buffer = self.graph[i].plot(self.x, self.y[i], pen=self.pen[i], symbol='o', symbolSize=3, symbolBrush='k')
                    self.graphData.append(buffer)
            self.plottingButtonState = True
            self.thread.plotting = True
            self.plotButton.setText("Disable Plotting")
            self.plotButton.repaint()
        else:
            self.plottingButtonState = False
            self.thread.plotting = False
            for i in self.graph:
                i.clear()
            self.plotButton.setText("Enable Plotting")
            self.plotButton.repaint()
        
    
    def textArrayToString(self, textArray):
        buffer = ""
        if(self.timeStampCheckBox.isChecked()):
            for text in textArray:
                buffer = buffer + time.ctime() + " : " + text
        else:
            for text in textArray:
                buffer = buffer + text
        return buffer

    def updateMonitor(self):
        self.nGraphs = self.thread.nGraphs
        self.textBrowserText = self.textBrowserText + self.thread.text
        if(len(self.textBrowserText) > 500):
            self.textBrowserText = self.textBrowserText[-500: ]
        self.textBrowser.setText(self.textBrowserText)
        self.textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.textBrowser.repaint()

    def updatePlot(self):
        for i in range(self.nGraphs):
            self.y[i] = np.append([self.thread.y[i]], self.y[i][:-1], axis=0)
            self.graphData[i].setData(self.x, self.y[i])



    
    # def onPressedSendButtonLeft(self):
    #     x = True
    #     try:
    #         self.thread_left
    #     except:
    #         x = False

    #     if(x):
    #         if(self.thread_left.isRunning()):
    #             self.textBrowserText_left = str(self.textBrowserText_left) + "Me: " + str(self.sendLine_left.text()) + "\n"
    #             self.textBrowser_left.setText(self.textBrowserText_left)
    #             self.thread_left.send(str(self.sendLine_left.text()))
    #             self.textBrowser_left.repaint()
    #         else:
    #             msg = QMessageBox()
    #             msg.setWindowTitle("ERROR")
    #             msg.setText("You are not connected to any Device!")
    #             x = msg.exec_()  # this will show our messagebox
    #     else:
    #         msg = QMessageBox()
    #         msg.setWindowTitle("ERROR")
    #         msg.setText("You are not connected to any Device!")
    #         x = msg.exec_()  # this will show our messagebox



App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())
