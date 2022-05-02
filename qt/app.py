#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 21:07:09 2022

@author: stuart
"""


import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QComboBox, QSlider, QLabel, 
                             QPushButton, QToolBar, QAction, QFileDialog,
                             QLabel, qApp)
from PyQt5.QtGui import QPalette, QColor, QPixmap
from PyQt5.QtCore import Qt

from enum import Enum
class State(Enum):
    NO_INPUT        = 1
    READY_TO_GORE   = 2
    CALCULATING     = 3
    UNSAVED_CHANGES = 4
    SAVED_CHANGES   = 5

class ImageLabel(QLabel):
    def __init__(self, text):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n {0} \n\n'.format(text))
        self.setStyleSheet('''
            QLabel{
                border: 2px dashed #aaa;
                font: italic
            }
        ''')

    def setPixmap(self, image):
        super().setPixmap(image)
        w = super().width();
        h = super().height();
        
        super().setScaledContents(1)

        # set a scaled pixmap to a w x h window keeping its aspect ratio 
        super().setPixmap(image.scaled(w, h, Qt.KeepAspectRatio));

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Gored Sim Eye")
        
        # allow drap & drop
        self.setAcceptDrops(True)

        # individual control layouts
        focalLengthLayout = QHBoxLayout()
        fundusImageSizeLayout = QHBoxLayout()
        numberOfGoresLayout = QHBoxLayout()
        retinalSizeLayout = QHBoxLayout()
        noCutAreaLayout = QHBoxLayout()
        rotationLayout = QHBoxLayout()
        qualityLayout = QHBoxLayout()
        buttonLayout = QHBoxLayout()
        
        # overall layout
        layout = QHBoxLayout()

        # LHS layout
        leftLayout = QVBoxLayout()
        
        # RHS layout
        rightLayout = QVBoxLayout()
        
        #starting values
        self.focalLengthValue = 24
        self.fundusImageSizeValue = 32
        self.numberOfGoresValue = 6
        self.retinalSizeValue = 100
        self.noCutAreaValue = 10
        self.rotationValue = 0
        self.qualityValue = 20
        self.imagePath = ""
        
        # control labels
        self.focalLengthLabel = QLabel("Focal length: {0}\u00b0".format(self.focalLengthValue))
        self.fundusImageSizeLabel = QLabel("Fundus image size: {0}\u00b0".format(self.fundusImageSizeValue))
        self.numberOfGoresLabel = QLabel("Number of gores: {0}".format(self.numberOfGoresValue))
        self.retinalSizeLabel = QLabel("Retinal size: {0}\u00b0".format(self.retinalSizeValue))
        self.noCutAreaLabel = QLabel("No-cut area: {0}\u00b0".format(self.noCutAreaValue))
        self.rotationLabel = QLabel("Rotation: {0}\u00b0".format(self.rotationValue * 0.5))
        self.qualityLabel = QLabel("Quality: {0}%".format(self.qualityValue))

        # create sliders
        self.focalLengthWidget = QSlider(Qt.Horizontal)
        self.fundusImageSizeWidget = QSlider(Qt.Horizontal)
        self.numberOfGoresWidget = QSlider(Qt.Horizontal)
        self.retinalSizeWidget = QSlider(Qt.Horizontal)
        self.noCutAreaWidget = QSlider(Qt.Horizontal)
        self.rotationWidget = QSlider(Qt.Horizontal)
        self.qualityWidget = QSlider(Qt.Horizontal)
        
        # create buttons
        self.goreButtonWidget = QPushButton("Gore")
        self.goreButtonWidget.setEnabled(False)
        self.cancelButtonWidget = QPushButton("Cancel")
        self.cancelButtonWidget.setEnabled(False)
        
        # create input + output image ImageLabel
        self.inputImageLabel = ImageLabel("Drop image here")
        self.outputImageLabel = ImageLabel("Output preview")
        
        # add sliders and button to LHS
        focalLengthLayout.addWidget(self.focalLengthLabel)
        focalLengthLayout.addWidget(self.focalLengthWidget)
        leftLayout.addLayout(focalLengthLayout)
        
        fundusImageSizeLayout.addWidget(self.fundusImageSizeLabel)
        fundusImageSizeLayout.addWidget(self.fundusImageSizeWidget)
        leftLayout.addLayout(fundusImageSizeLayout)
        
        numberOfGoresLayout.addWidget(self.numberOfGoresLabel)
        numberOfGoresLayout.addWidget(self.numberOfGoresWidget)
        leftLayout.addLayout(numberOfGoresLayout)
        
        retinalSizeLayout.addWidget(self.retinalSizeLabel)
        retinalSizeLayout.addWidget(self.retinalSizeWidget)
        leftLayout.addLayout(retinalSizeLayout)
        
        noCutAreaLayout.addWidget(self.noCutAreaLabel)
        noCutAreaLayout.addWidget(self.noCutAreaWidget)
        leftLayout.addLayout(noCutAreaLayout)
        
        rotationLayout.addWidget(self.rotationLabel)
        rotationLayout.addWidget(self.rotationWidget)
        leftLayout.addLayout(rotationLayout)
        
        qualityLayout.addWidget(self.qualityLabel)
        qualityLayout.addWidget(self.qualityWidget)
        leftLayout.addLayout(qualityLayout)
        
        buttonLayout.addWidget(self.goreButtonWidget)
        buttonLayout.addWidget(self.cancelButtonWidget)
        leftLayout.addLayout(buttonLayout)
        
        # add previews to RHS
        rightLayout.addWidget(self.inputImageLabel)
        rightLayout.addWidget(self.outputImageLabel)
        
        # add LHS + RHS to overall layout
        layout.addLayout(leftLayout, 1)
        layout.addLayout(rightLayout, 2)

        # set slider ranges, steps
        self.focalLengthWidget.setRange(5,50)
        self.focalLengthWidget.setSingleStep(1)
        
        self.fundusImageSizeWidget.setRange(5,100)
        self.fundusImageSizeWidget.setSingleStep(1)
        
        self.numberOfGoresWidget.setRange(3,24)
        self.numberOfGoresWidget.setSingleStep(1)
        
        self.retinalSizeWidget.setRange(10,150)
        self.retinalSizeWidget.setSingleStep(1)
        
        self.noCutAreaWidget.setRange(0,90)
        self.noCutAreaWidget.setSingleStep(1)
        
        self.rotationWidget.setRange(0,720)
        self.rotationWidget.setSingleStep(1)
        
        self.qualityWidget.setRange(10,100)
        self.qualityWidget.setSingleStep(1)
        
        # initial values
        self.focalLengthWidget.setValue(self.focalLengthValue)
        self.fundusImageSizeWidget.setValue(self.fundusImageSizeValue)
        self.numberOfGoresWidget.setValue(self.numberOfGoresValue)
        self.retinalSizeWidget.setValue(self.retinalSizeValue)
        self.noCutAreaWidget.setValue(self.noCutAreaValue)
        self.rotationWidget.setValue(self.rotationValue)
        self.qualityWidget.setValue(self.qualityValue)

        # connect input widgets with slots
        self.focalLengthWidget.valueChanged.connect(self.value_changed)
        self.focalLengthWidget.sliderMoved.connect(self.slider_position)
        self.focalLengthWidget.sliderPressed.connect(self.slider_pressed)
        self.focalLengthWidget.sliderReleased.connect(self.slider_released)
        
        self.fundusImageSizeWidget.valueChanged.connect(self.value_changed)
        self.fundusImageSizeWidget.sliderMoved.connect(self.slider_position)
        self.fundusImageSizeWidget.sliderPressed.connect(self.slider_pressed)
        self.fundusImageSizeWidget.sliderReleased.connect(self.slider_released)
        
        self.numberOfGoresWidget.valueChanged.connect(self.value_changed)
        self.numberOfGoresWidget.sliderMoved.connect(self.slider_position)
        self.numberOfGoresWidget.sliderPressed.connect(self.slider_pressed)
        self.numberOfGoresWidget.sliderReleased.connect(self.slider_released)
        
        self.retinalSizeWidget.valueChanged.connect(self.value_changed)
        self.retinalSizeWidget.sliderMoved.connect(self.slider_position)
        self.retinalSizeWidget.sliderPressed.connect(self.slider_pressed)
        self.retinalSizeWidget.sliderReleased.connect(self.slider_released)
        
        self.noCutAreaWidget.valueChanged.connect(self.value_changed)
        self.noCutAreaWidget.sliderMoved.connect(self.slider_position)
        self.noCutAreaWidget.sliderPressed.connect(self.slider_pressed)
        self.noCutAreaWidget.sliderReleased.connect(self.slider_released)
        
        self.rotationWidget.valueChanged.connect(self.value_changed)
        self.rotationWidget.sliderMoved.connect(self.slider_position)
        self.rotationWidget.sliderPressed.connect(self.slider_pressed)
        self.rotationWidget.sliderReleased.connect(self.slider_released)
        
        self.qualityWidget.valueChanged.connect(self.value_changed)
        self.qualityWidget.sliderMoved.connect(self.slider_position)
        self.qualityWidget.sliderPressed.connect(self.slider_pressed)
        self.qualityWidget.sliderReleased.connect(self.slider_released)
        
        self.goreButtonWidget.clicked.connect(self.gore_handler)
        self.cancelButtonWidget.clicked.connect(self.cancel_handler)
        
        # the menubar
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('File')

        # the menu actions
        openAction = QAction('&Open input image...', self)  
        openAction.triggered.connect(self.open_handler) 
        saveAction = QAction('&Save', self)
        saveAction.setEnabled(False)
        saveAction.triggered.connect(self.save_forwarder)
        saveAsAction = QAction('S&ave as...', self)
        saveAsAction.setEnabled(False)
        saveAsAction.triggered.connect(self.save_as_forwarder)
        exitAction = QAction('&Exit', self)
        exitAction.triggered.connect(self.exit_handler)
        
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(saveAsAction)
        fileMenu.addAction(exitAction)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        self.state = State.NO_INPUT
        
    def open_handler(self):
        self.imagePath, _ = QFileDialog.getOpenFileName()
        pixmap = QPixmap(self.imagePath)
        self.inputImageLabel.setPixmap(pixmap)
        
    def save_forwarder(self):
        self.save_handler(False)
        
    def save_as_forwarder(self):
        self.save_handler(True)
        
    def save_handler(self, save_as):
        print (self.sender().text())
        print (save_as)
        
    def exit_handler(self):
        if (self.state == State.NO_INPUT or
            self.state == State.READY_TO_GORE or
            self.state == State.SAVED_CHANGES):
            qApp.quit()
        elif (self.state == State.CALCULATING):
            pass # TODO: Prompt
        elif (self.state == State.UNSAVED_CHANGES):
            pass # TODO: Prompt
        else:
            pass # error
             
    def gore_handler(self):
        pass
    
    def cancel_handler(self):
        pass
        
    def value_changed(self, i):
        if (self.sender() == self.focalLengthWidget):
            self.focalLengthLabel.setText("Focal length: {0}\u00b0".format(i))
            self.focalLengthValue = i
        elif (self.sender() == self.fundusImageSizeWidget):
            self.fundusImageSizeLabel.setText("Image extent: {0}\u00b0".format(i))
            self.fundusImageSizeValue = i
        elif (self.sender() == self.numberOfGoresWidget):
            self.numberOfGoresLabel.setText("No. gores: {0}".format(i))
            self.numberOfGoresValue = i
        elif (self.sender() == self.retinalSizeWidget):
            self.retinalSizeLabel.setText("Retinal size: {0}\u00b0".format(i))
            self.retinalSizeValue = i
        elif (self.sender() == self.noCutAreaWidget):
            self.noCutAreaLabel.setText("No-cut area: {0}\u00b0".format(i))
            self.noCutAreaValue = i
        elif (self.sender() == self.rotationWidget):
            self.rotationLabel.setText("Rotation: {0}\u00b0".format(i * 0.5))
            self.rotationValue = i
        elif (self.sender() == self.qualityWidget):
            self.qualityLabel.setText("Quality: {0}%".format(i))
            self.qualityValue = i

    def slider_position(self, p):
        #print("position", p)
        pass

    def slider_pressed(self):
        #print("Pressed!")
        pass

    def slider_released(self):
        #print("Released")
        pass
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.set_image(file_path)

            event.accept()
        else:
            event.ignore()

    def set_image(self, file_path):
        self.imagePath = file_path
        self.inputImageLabel.setPixmap(QPixmap(file_path))
        
    def calculate(self):
        sys.sleep(5)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit( app.exec_() )