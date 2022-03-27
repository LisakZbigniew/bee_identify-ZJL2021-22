import sys
from turtle import update

from PyQt5.QtWidgets import QApplication, QSpinBox,QFileDialog , QWidget, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy, QMainWindow, QAction, QLabel
from PyQt5.QtGui import QKeySequence, QMouseEvent
from PyQt5.QtCore import pyqtSlot,Qt
from matplotlib.backend_bases import MouseEvent, MouseButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np
import random
import math
from photo import Photo


class App(QMainWindow):

    NAMES_DELIMITER = ';'

    def __init__(self):
        super().__init__()

        self.title = 'Image sampling'

        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480

        self.file_list = np.array([])
        self.current_index = -1
        self.arrowWidth = 30
        
        self.leftButton = None
        self.rightButton = None
        self.startLabel = None
        self.endLabel = None
        self.photoCanvas = None
        self.sampleInput = None
        self.sampleSide = None
        self.sampleNamesInput = None

        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        self.setUpMenu()
        self.createVerticalLayout()

        self.show()

    def setUpMenu(self):
        menu = self.menuBar()
        file = menu.addMenu('File')

        addFilesButton = QAction('Open files',file)
        addFilesButton.setShortcut(QKeySequence.Open)
        addFilesButton.setStatusTip("Open files for processing")
        addFilesButton.triggered.connect(self.addFiles)

        file.addAction(addFilesButton)

    def createVerticalLayout(self):
        layout = QVBoxLayout()
        centralWidget = QWidget()

        layout.addWidget(self.createPhotoSection())
        layout.addWidget(self.createFormSection())

        
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
    
    def createPhotoSection(self):
        widget = QWidget()
        layout = QHBoxLayout()

        self.leftButton = QPushButton("<")
        self.leftButton.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding)
        self.leftButton.setMaximumWidth(self.arrowWidth)
        self.leftButton.clicked.connect(self.left_click)

        layout.addWidget(self.leftButton)

        self.photoCanvas = PlotCanvas(parent = self)
        layout.addWidget(self.photoCanvas)        

        self.rightButton = QPushButton(">")
        self.rightButton.setSizePolicy(QSizePolicy.Policy.Minimum,QSizePolicy.Policy.Expanding)
        self.rightButton.setMaximumWidth(self.arrowWidth)
        self.rightButton.clicked.connect(self.right_click)

        layout.addWidget(self.rightButton)

        self.updateScrollButtons()

        widget.setLayout(layout)
        return widget
    
    def createFormSection(self):
        widget = QWidget()
        layout = QGridLayout()

        self.startLabel = QLabel("Start point: (-,-)")   
        layout.addWidget(self.startLabel,0,1)

        self.endLabel = QLabel("End point: (-,-)")   
        layout.addWidget(self.endLabel,0,3)

        resetZoomButton = QPushButton("Reset zoom")
        resetZoomButton.clicked.connect(self.resetZoomClick)
        layout.addWidget(resetZoomButton,2,1)

        resetPointsButton = QPushButton("Reset points")
        resetPointsButton.clicked.connect(self.resetPointsClick)
        layout.addWidget(resetPointsButton,2,3)

        sampleLabel = QLabel("Number of samples:")
        layout.addWidget(sampleLabel,4,1)
        
        self.sampleInput = QSpinBox()
        self.sampleInput.setMinimum(2)
        self.sampleInput.textChanged.connect(self.recalculateSamples)
        layout.addWidget(self.sampleInput,4,3)

        sampleSizeLabel = QLabel("Size of samples:")
        layout.addWidget(sampleSizeLabel,6,1)

        self.sampleSide = QSpinBox()
        self.sampleSide.setMinimum(1)
        self.sampleSide.setSingleStep(2)
        layout.addWidget(self.sampleSide,6,3)

        sampleNamesLabel = QLabel("Lables for samples(';' separated):")
        layout.addWidget(sampleNamesLabel,8,1)

        self.sampleNamesInput = QTextEdit()
        self.sampleNamesInput.setAcceptRichText(False)
        layout.addWidget(self.sampleNamesInput,8,3)


        confirmButton = QPushButton("Save Samples")
        confirmButton.clicked.connect(self.saveSamples)
        layout.addWidget(confirmButton,9,1,1,3)

        layout.setColumnMinimumWidth(2,20)

        widget.setLayout(layout)
        return widget

    @pyqtSlot()
    def left_click(self):
        self.current_index = max(0, self.current_index - 1)
        self.photoChanged()
        
    @pyqtSlot()
    def right_click(self):
        self.current_index = min(self.file_list.size - 1, self.current_index + 1)
        self.photoChanged()
        

    @pyqtSlot()
    def addFiles(self):
        files, _ = QFileDialog.getOpenFileNames(self,
                                     "Select one or more files to open",
                                     ".",
                                     "Bee Photos (*.np)")
        self.file_list = np.array([Photo.create(file) for file in files])
        print(self.file_list)
        self.file_list = self.file_list[self.file_list != np.array(None)]
        print(self.file_list)
        self.current_index = min(self.file_list.size - 1,0)
        self.photoChanged()
        
    @pyqtSlot()
    def resetZoomClick(self):
        print("Reset Zoom")
        if(self.current_index != -1):
            self.file_list[self.current_index].resetZoom()
            self.photoChanged()


    @pyqtSlot()
    def resetPointsClick(self):
        print("Reset points")
        if(self.current_index != -1):
            self.file_list[self.current_index].start_point = (-1,-1)
            self.file_list[self.current_index].end_point = (-1,-1)
            self.photoChanged()

    @pyqtSlot()
    def recalculateSamples(self):
        print("Recalculating samples")
        self.photoChanged()

    @pyqtSlot()
    def saveSamples(self):
        print("Saving samples")
        names = self.sampleNamesInput.toPlainText().split(self.NAMES_DELIMITER)
        self.file_list[self.current_index].saveSamples(self.sampleInput.value(),self.sampleSide.value(),names)

    def updateScrollButtons(self):
        if(self.current_index == -1 or self.current_index == 0):
            self.leftButton.setDisabled(True)
        else:
            self.leftButton.setDisabled(False)
        
        if(self.current_index == -1 or self.current_index == self.file_list.size-1):
            self.rightButton.setDisabled(True)
        else:
            self.rightButton.setDisabled(False)

        #print(self.current_index)

    def updateLabels(self):
        startString = "Start point: "
        endString = "End point: "
        if self.current_index != -1:
            if(self.file_list[self.current_index].start_point != (-1,-1)):
                startString += str(self.file_list[self.current_index].start_point)
            else:
                startString += "(-,-)"
            
            if(self.file_list[self.current_index].end_point != (-1,-1)):
                endString += str(self.file_list[self.current_index].end_point)
            else:
                endString += "(-,-)"
        else:
            startString+= "(-,-)"
            endString+= "(-,-)"
        self.startLabel.setText(startString)
        self.endLabel.setText(endString)


    def photoChanged(self):
        self.updateScrollButtons()
        self.updateLabels()
        self.photoCanvas.plot()

class PlotCanvas(FigureCanvas):

    def __init__(self, parent : App, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_tight_layout(True)
        self.parent = parent
        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self,
                QSizePolicy.MinimumExpanding,
                QSizePolicy.MinimumExpanding)
        FigureCanvas.updateGeometry(self)
        FigureCanvas.mpl_connect(self,'button_press_event', self.on_press)
        self.ax = self.figure.add_subplot(111)
        self.plot()


    def plot(self):
        data = np.array([random.random() for i in range(30)])
        data *= 2000
        self.ax.cla() 
        self.ax.set_axis_off()
        if(self.parent.current_index != -1):
            photo = self.parent.file_list[self.parent.current_index]
            d = photo.getVisibleImage()
            d[d>255]=255
            self.ax.imshow(d.astype(int))
            
            points = photo.getCurrentlyVisibleSamples(self.parent.sampleInput.value())
            for point in points :
                self.ax.scatter([point[0]],[point[1]],c='y',marker = 'x')

            start = photo.getVisibleStart()
            if(start != None):
                self.ax.scatter([start[0]],[start[1]],c='b',marker = 'x')

            end = photo.getVisibleEnd()
            if(end != None):
                self.ax.scatter([end[0]],[end[1]],c='r',marker = 'x')

            self.ax.set_title(photo.photo_data['filename'])
        self.draw()

    def on_press(self, event):
        if(self.parent.current_index == -1):
            return
        #print("Pressed " ,event.button)
        #print(event.xdata,event.ydata)
        if(event.button == MouseButton.RIGHT):            
            self.parent.file_list[self.parent.current_index].setCenter(int(event.xdata),int(event.ydata))
            self.parent.file_list[self.parent.current_index].zoom *=2

        if(event.button == MouseButton.MIDDLE):
            self.parent.file_list[self.parent.current_index].resetZoom()

        if(event.button == MouseButton.LEFT):
            self.parent.file_list[self.parent.current_index].mark(int(event.xdata),int(event.ydata))
            self.parent.photoChanged()
        self.plot() 


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
