#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 21:07:09 2022

@author: stuart
"""

from PyQt5.QtWidgets import (QApplication, 
                             QMainWindow, 
                             QWidget, 
                             QHBoxLayout, 
                             QVBoxLayout,
                             QSlider, 
                             QLabel, 
                             QPushButton,
                             QAction, 
                             QFileDialog,
                             QToolTip,
                             QSizePolicy,
                             qApp)
from PyQt5.QtWidgets import QMessageBox as qm
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal

from time import sleep
import logging, sys, os
sys.path.append("../gore")
import gore2
from PIL.ImageQt import ImageQt
from enum import Enum

class State(Enum):
    # Class defining FSM states
    START                       = 0
    NO_INPUT                    = 1
    READY_TO_GORE               = 2
    CALCULATING                 = 3
    CALCULATING_UNSAVED_CHANGES = 4
    CALCULATING_SAVED_CHANGES   = 5
    CANCELLING                  = 6
    CANCELLING_UNSAVED_CHANGES  = 7
    CANCELLING_SAVED_CHANGES    = 8
    UNSAVED_CHANGES             = 9
    SAVED_CHANGES               = 10
    END                         = 11
    NUMBER_OF_STATES            = 12

class ImageLabel(QLabel):
    # Class to display image preview windows
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
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)
        
    def heightForWidth(self, width):
        return width

    def setPixmap(self, image):
        super().setPixmap(image)
        w = super().width()
        h = super().height()
        
        super().setScaledContents(1)

        # set a scaled pixmap to a w x h window keeping its aspect ratio 
        super().setPixmap(image.scaled(w, h, Qt.KeepAspectRatio))

class MainWindow(QMainWindow):
    # Class for main window

    def __init__(self):
        super(MainWindow, self).__init__()
        
        # setup debugging
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logging.debug('Debugging Gored Sim Eye!')

        # window title
        self.setWindowTitle("Gored Sim Eye")
        
        # define thread and worker objects
        self.thread = None
        self.worker = None
        
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
        
        # create overall layout
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
        self.imagePath = None
        self.outputPath = None
        
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
        
        # create tooltips
        self.focalLengthWidget.setToolTip('This is the focal length')
        self.fundusImageSizeWidget.setToolTip('This is the fundus image size')
        self.numberOfGoresWidget.setToolTip('This is the number of gores')
        self.retinalSizeWidget.setToolTip('This is the retinal size')
        self.noCutAreaWidget.setToolTip('This is the no-cut area')
        self.rotationWidget.setToolTip('This is the rotation')
        self.qualityWidget.setToolTip('This is the quality')
        
        # create buttons
        self.goreButtonWidget = QPushButton()
        
        # create input + output image ImageLabel
        self.previewImageLabel = ImageLabel("Drop image here")
        
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
        leftLayout.addLayout(buttonLayout)
        
        # add previews to RHS
        rightLayout.addWidget(self.previewImageLabel)
        
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
        
        self.goreButtonWidget.clicked.connect(self.gore_cancel_handler)
        
        # the menubar
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('File')

        # the menu actions - members so they can be updated later
        self.openAction = QAction('&Open input image...', self)  
        self.openAction.triggered.connect(self.open_handler) 
        self.saveAction = QAction('&Save', self)
        self.saveAction.triggered.connect(self.save_forwarder)
        self.saveAsAction = QAction('S&ave as...', self)
        self.saveAsAction.triggered.connect(self.save_as_forwarder)
        self.exitAction = QAction('&Exit', self)
        self.exitAction.triggered.connect(self.exit_handler)
        
        # add the actions
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addAction(self.exitAction)

        # create "the" widget and set the layout
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        # initialise the FSM
        self.state = State.START
        self.transition(State.NO_INPUT)
        self.update_widgets()
        
    def open_image_dialog(self):
        # returns true if a valid image filename was set
        fileFilter = "Image files (*.jpg *.gif *.png *.bmp *.tiff)"
        fileName, _ = QFileDialog.getOpenFileName(self, 
                                                'Open file', 
                                                os.getcwd(),
                                                fileFilter)
        if (fileName != ""):
            self.imagePath = fileName
            pixmap = QPixmap(self.imagePath)
            self.previewImageLabel.setPixmap(pixmap)
            return True
        else:
            return False
    
    def save_output_dialog(self):
        # returns true if an image was saved successfuly
        fileFilter = "Image files (*.jpg *.gif *.png *.bmp *.tiff)"
        fileName, _ = QFileDialog.getSaveFileName(self,
                                                  'Save file',
                                                  os.getcwd(),
                                                  fileFilter)
        if (fileName != ""):
            self.outputPath = fileName
            return self.save_output()
        else:
            return False
    
    def save_output(self):
        return self.worker.outputPixmap.save(self.outputPath, "PNG")
    
    def start_calculating(self):
        self.runLongTask()
        
    def stop_calculating(self):
        pass #todo
    
    def raise_state_exception(self):
        caller = sys._getframe(1).f_code.co_name
        raise Exception("{0} unexpected in {1}".format(self.state, caller))
        
    def transition(self, newState = None):
        # transition the main FSM
        caller = sys._getframe(1).f_code.co_name
        if (newState != None):
            logging.debug("State transition: %s => %s in %s", self.state, newState, caller)
            self.state = newState
        else:
            logging.debug("No transition: %s in %s", self.state, caller)
            
    def update_widgets(self):
        # update the menu items and the gore/cancel button
        if (self.state ==  State.START):
            self.openAction.setEnabled(False)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(False)
            self.goreButtonWidget.setText("")
        elif (self.state == State.NO_INPUT):
            self.openAction.setEnabled(True)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(False)
            self.goreButtonWidget.setText("Gore")
        elif (self.state == State.READY_TO_GORE):
            self.openAction.setEnabled(True)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(True)
            self.goreButtonWidget.setText("Gore")
        elif (self.state == State.CALCULATING):
            self.openAction.setEnabled(False)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(True)
            self.goreButtonWidget.setText("Cancel")    
        elif (self.state == State.CALCULATING_UNSAVED_CHANGES):
            self.openAction.setEnabled(False)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(True)
            self.goreButtonWidget.setText("Cancel")
        elif (self.state == State.CALCULATING_SAVED_CHANGES):
            self.openAction.setEnabled(False)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(True)
            self.goreButtonWidget.setText("Cancel")      
        elif (self.state == State.CANCELLING):
            self.openAction.setEnabled(False)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(False)
            self.goreButtonWidget.setText("Cancel")
        elif (self.state == State.CANCELLING_UNSAVED_CHANGES):
            self.openAction.setEnabled(False)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(False)
            self.goreButtonWidget.setText("Cancel")
        elif (self.state == State.CANCELLING_SAVED_CHANGES):
            self.openAction.setEnabled(False)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(False)
            self.goreButtonWidget.setText("Cancel")
        elif (self.state == State.UNSAVED_CHANGES):
            self.openAction.setEnabled(True)
            self.saveAction.setEnabled(True)
            self.saveAsAction.setEnabled(True)
            self.goreButtonWidget.setEnabled(True)
            self.goreButtonWidget.setText("Gore")
        elif (self.state == State.SAVED_CHANGES):
            self.openAction.setEnabled(True)
            self.saveAction.setEnabled(True)
            self.saveAsAction.setEnabled(True)
            self.goreButtonWidget.setEnabled(True)
            self.goreButtonWidget.setText("Gore")
        elif (self.state == State.UNSAVED_CHANGES):
            self.openAction.setEnabled(True)
            self.saveAction.setEnabled(True)
            self.saveAsAction.setEnabled(True)
            self.goreButtonWidget.setEnabled(True)
            self.goreButtonWidget.setText("Gore")
        else:
            # invalid state: do nothing
            pass
        
    def open_handler(self):
        if (self.state == State.NO_INPUT or
            self.state == State.READY_TO_GORE):
            if (self.open_image_dialog()):
                self.transition(State.READY_TO_GORE)
            else:
                self.transition()
        elif (self.state == State.SAVED_CHANGES):
            if (self.open_image_dialog()):
                self.outputPath = None
                self.transition(State.READY_TO_GORE)
            else:
                self.transition()
        elif (self.state == State.CALCULATING or
              self.state == State.CALCULATING_UNSAVED_CHANGES or
              self.state == State.CALCULATING_SAVED_CHANGES or
              self.state == State.CANCELLING or
              self.state == State.CANCELLING_UNSAVED_CHANGES or
              self.state == State.CANCELLING_SAVED_CHANGES or
              self.state == State.START or
              self.state == State.END):
            self.raise_state_exception()
        elif (self.state == State.UNSAVED_CHANGES):
            ret = qm.question(self,'', "Unsaved changes: open new image and lose changes?", qm.Yes | qm.No)
            if (ret == qm.Yes):
                if (self.open_image_dialog()):
                    self.transition(State.READY_TO_GORE)
                    self.outputPath = None
                else:
                    self.transition()
            else:
                self.transition()
        else:
            # invalid state
            self.raise_state_exception()
            
        self.update_widgets()
        
    def save_forwarder(self):
        # forward call from "Save" action to common handler
        self.save_handler(False)
        
    def save_as_forwarder(self):
        # forward call from "Save As" action to common handler
        self.save_handler(True)
        
    def save_handler(self, save_as):
        if (self.state == State.NO_INPUT or 
            self.state == State.READY_TO_GORE or 
            self.state == State.CALCULATING or
            self.state == State.CALCULATING_UNSAVED_CHANGES or
            self.state == State.CALCULATING_SAVED_CHANGES or
            self.state == State.CANCELLING or
            self.state == State.CANCELLING_UNSAVED_CHANGES or
            self.state == State.CANCELLING_SAVED_CHANGES or
            self.state == State.START or
            self.state == State.END):
            self.raise_state_exception()
        elif (self.state == State.UNSAVED_CHANGES):
            if (save_as or self.outputPath == None):    
                if (self.save_output_dialog()):
                    self.transition(State.SAVED_CHANGES)
                else:
                    self.transition()
            else:
                if (self.save_output()):
                    self.transition(State.SAVED_CHANGES)
                else:
                    self.transition()
        elif (self.state == State.SAVED_CHANGES):
            if (save_as):
                self.save_output_dialog()
            self.transition()
        else:
            self.raise_state_exception()
            
        self.update_widgets()
            
    def exit_handler(self):
        if (self.state == State.NO_INPUT or
            self.state == State.READY_TO_GORE or
            self.state == State.SAVED_CHANGES or
            self.state == State.CANCELLING or
            self.state == State.CANCELLING_UNSAVED_CHANGES):
            self.transition(State.END)
            qApp.quit()
        elif (self.state == State.CALCULATING or
              self.state == State.CALCULATING_SAVED_CHANGES):
            ret = qm.question(self,'', "Calculation running: really exit?", qm.Yes | qm.No)
            if (ret == qm.Yes):
                self.transition(State.END)
                qApp.quit()  
            else:
                self.transition()
        elif (self.state == State.CALCULATING_UNSAVED_CHANGES):
            ret = qm.question(self,'', "Calculation running: exit and lose unsaved changes?", qm.Yes | qm.No)
            if (ret == qm.Yes):
                self.transition(State.END)
                qApp.quit()
            else:
                self.transition()
        elif (self.state == State.UNSAVED_CHANGES or
              self.state == State.CANCELLING_SAVED_CHANGES):
            ret = qm.question(self,'', "Unsaved changes: exit and lose changes?", qm.Yes | qm.No)
            if (ret == qm.Yes):
                self.transition(State.END)
                qApp.quit()
            else:
                self.transition()
        elif (self.state == State.START or
              self.state == State.END):
            self.raise_state_exception()
        else:
            # invalid state
            self.raise_state_exception()
            
        self.update_widgets()
             
    def gore_cancel_handler(self):
        # handle button press: both gore and cancel
        if (self.state == State.NO_INPUT):
            self.raise_state_exception()
        elif (self.state == State.READY_TO_GORE or
              self.state == State.UNSAVED_CHANGES or
              self.state == State.SAVED_CHANGES):
            self.transition(State.CALCULATING)
            self.goreButtonWidget.setText('Cancel')
            self.start_calculating()
        elif (self.state == State.CALCULATING): # cancel requested
            self.thread.requestInterruption()
            self.transition(State.CANCELLING)
        elif (self.state == State.CALCULATING_UNSAVED_CHANGES): #cancel requested
            self.thread.requestInterruption()
            self.transition(State.CANCELLING_UNSAVED_CHANGES)
        elif (self.state == State.CALCULATING_SAVED_CHANGES): #cancel requested
            self.thread.requestInterruption()
            self.transition(State.CANCELLING_SAVED_CHANGES)
        elif (self.state == State.CANCELLING or
              self.state == State.CANCELLING_UNSAVED_CHANGES or
              self.state == State.CANCELLING_SAVED_CHANGES):
            self.transition()
        elif (self.state == State.START or
              self.state == State.END):
            self.raise_state_exception()
        else:
            # invalid state
            self.raise_state_exception()
            
        self.update_widgets()
            
    def calculation_complete_forwarder(self):
        # forward calls from thread.finished() depending on whether calculation
        # completed or was cancelled
        if (self.worker.complete):
            self.calculation_complete_handler()
        else:
            self.calculation_cancelled_handler()
            
    def calculation_complete_handler(self):
        if (self.state == State.NO_INPUT or
            self.state == State.READY_TO_GORE or
            self.state == State.UNSAVED_CHANGES or
            self.state == State.SAVED_CHANGES or
            self.state == State.CANCELLING or
            self.state == State.CANCELLING_UNSAVED_CHANGES or
            self.state == State.CANCELLING_SAVED_CHANGES):
            self.raise_state_exception()
            self.transition()
        elif (self.state == State.CALCULATING or
              self.state == State.CALCULATING_UNSAVED_CHANGES or
              self.state == State.CALCULATING_SAVED_CHANGES):
            self.previewImageLabel.setPixmap(self.worker.outputPixmap)
            self.transition(State.UNSAVED_CHANGES)
        elif (self.state == State.START or
              self.state == State.END):
            self.raise_state_exception()
        else:
            # invalid state
            self.raise_state_exception()
            
        self.update_widgets()
                
    def calculation_cancelled_handler(self):
        if (self.state == State.NO_INPUT or
            self.state == State.START or               
            self.state == State.NO_INPUT or                  
            self.state == State.READY_TO_GORE or
            self.state == State.CALCULATING or
            self.state == State.CALCULATING_UNSAVED_CHANGES or
            self.state == State.CALCULATING_SAVED_CHANGES or
            self.state == State.UNSAVED_CHANGES or
            self.state == State.SAVED_CHANGES or
            self.state == State.END):
            self.raise_state_exception()
        elif (self.state == State.CANCELLING):
            self.transition(State.READY_TO_GORE)
        elif (self.state == State.CANCELLING_UNSAVED_CHANGES):
            self.transition(State.UNSAVED_CHANGES)
        elif (self.state == State.CANCELLING_SAVED_CHANGES):
            self.transition(State.SAVED_CHANGES)
        else:
            # invalid state
            self.raise_state_exception()
            
        self.update_widgets()
            
    def value_changed(self, i):
        # handle updates from the ui elements (sliders)
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
        pass

    def slider_pressed(self):
        pass

    def slider_released(self):
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
        self.previewImageLabel.setPixmap(QPixmap(file_path))
        
    def get_inputs(self):
        # collect the inputs to the calculation as a dict
        inputs = dict(image_path = self.imagePath, 
                      focal_length = self.focalLengthValue, 
                      alpha_max = gore2.deg2rad(self.fundusImageSizeValue), 
                      num_gores = self.numberOfGoresValue, 
                      phi_no_cut = gore2.deg2rad(self.noCutAreaValue),
                      rotation = self.rotationValue,
                      quality = self.qualityValue
                      )
        return inputs
        
    def runLongTask(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker(self.get_inputs())
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Step 6: Start the thread
        self.thread.start()

        # Final resets
        self.thread.finished.connect(
            self.calculation_complete_forwarder
        )
        
# Worker class
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    
    def __init__(self, inputs = None):
        QObject.__init__(self)
        self.complete = True
        self.inputs = inputs

    def run(self):
        """This is where we do the goring"""
        
        im = gore2.make_rotary_adjusted(**self.inputs)
        qim = ImageQt(im)
        pix = QPixmap.fromImage(qim)
        self.outputPixmap = pix
        
        for i in range(5):
            sleep(.1)
            logging.debug("calculating: %i", i)
            self.progress.emit(i + 1)
            if QThread.currentThread().isInterruptionRequested():
                logging.debug("Calcution CANCELLED")
                self.complete = False
                break
        
        self.finished.emit()

app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit( app.exec_() )