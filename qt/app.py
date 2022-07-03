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
                             QDoubleSpinBox,
                             QLabel, 
                             QPushButton,
                             QAction, 
                             QFileDialog,
                             QColorDialog,
                             QSizePolicy,
                             QSplashScreen,
                             QStatusBar,
                             qApp)
from PyQt5.QtWidgets import QMessageBox as qm
from PyQt5.QtGui import QPixmap, QKeySequence, QColor
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, QUrl, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
import qtawesome as qta

import logging, sys, os
sys.path.append("../gore")
from PIL.ImageQt import ImageQt
from enum import Enum
from numpy import pi
from time import perf_counter

aboutText ="""
About this software

Credits
"""

def deg2rad(x):
    """
    deg2rad:    return an angle give in degrees in radians

    x:          angle (degrees)
    
    returns:    angle (radians)
    """
    
    return x / 180 * pi

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

class Browser(QWebEngineView):
    def __init__(self):
        super().__init__()
        self.loadProgress.connect(logging.debug)
        dirPath = os.path.dirname(os.path.realpath(__file__))
        guidePath = os.path.join(dirPath,"userguide.html")
        self.load(QUrl.fromLocalFile(guidePath))
        self.loadFinished.connect(self.pageReady)

    def pageReady(self, success):
        if success:
            self.resize(640, 480)
        else:
            logging.debug('Browser: page failed to load')

class ImageLabel(QLabel):
    # Class to display image preview windows
    def __init__(self, text):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.text = text
        self.setText(text)
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
        self.clear()
        super().setPixmap(image)
        growthCorrectionInPixels = 4
        w = super().width() - growthCorrectionInPixels
        h = super().height() - growthCorrectionInPixels
        
        super().setScaledContents(1)

        # set a scaled pixmap to a w x h window keeping its aspect ratio
        super().setPixmap(image.scaled(w, h, Qt.KeepAspectRatio))
        
    def clearPixmap(self):
        self.clear()
        self.setText(self.text)

class MainWindow(QMainWindow):
    # Class for main window

    def __init__(self):
        super(MainWindow, self).__init__()
        
        # set up debugging
        if (len(sys.argv) > 1 and sys.argv[1] == "-d"):
            logLevel = logging.DEBUG
        else:
            logLevel = logging.FATAL    
        logging.basicConfig(stream=sys.stderr, level=logLevel)
        logging.debug('Debugging Gored Sim Eye!')
        
        #self.browser = Browser()

        # window title
        self.setWindowTitle("Gored Sim Eye")
        
        # status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        self.statusLabel = QLabel()
        self.statusBar.addPermanentWidget(self.statusLabel, 100)
        self.statusLabel.setText('')
        
        # define thread and worker objects
        self.thread = None
        self.worker = None
        
        # allow drap & drop
        self.setAcceptDrops(True)

        # individual control layouts
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
        self.fundusImageSizeValue = 60
        self.numberOfGoresValue = 6
        self.retinalSizeValue = 180
        self.noCutAreaValue = 20
        self.rotationValue = 0
        self.qualityValue = 20
        self.imagePath = None
        self.backgroundColour = QColor("white") # never reset; lost on exit
        self.outputPath = None
        
        # control labels
        self.fundusImageSizeLabel = QLabel("")
        self.numberOfGoresLabel = QLabel("")
        self.retinalSizeLabel = QLabel("")
        self.noCutAreaLabel = QLabel("")
        self.rotationLabel = QLabel("")
        self.qualityLabel = QLabel("")
        
        # update the labels
        self.update_inputs_text()

        # create sliders
        self.fundusImageSizeWidget = QSlider(Qt.Horizontal)
        self.fundusImageSizeWidget.setFixedWidth(150)
        self.numberOfGoresWidget = QSlider(Qt.Horizontal)
        self.numberOfGoresWidget.setFixedWidth(150)
        self.retinalSizeWidget = QSlider(Qt.Horizontal)
        self.retinalSizeWidget.setFixedWidth(150)
        self.noCutAreaWidget = QSlider(Qt.Horizontal)
        self.noCutAreaWidget.setFixedWidth(150)
        self.rotationWidget = QDoubleSpinBox()
        self.rotationWidget.setGeometry(100, 100, 150, 40)
        self.qualityWidget = QSlider(Qt.Horizontal)
        self.qualityWidget.setFixedWidth(150)
        
        # create tooltips
        self.fundusImageSizeWidget.setToolTip('This is the fundus image size')
        self.numberOfGoresWidget.setToolTip('This is the number of gores')
        self.retinalSizeWidget.setToolTip('This is the retinal size')
        self.noCutAreaWidget.setToolTip('This is the no-cut area')
        self.rotationWidget.setToolTip('This is the rotation')
        self.qualityWidget.setToolTip('This is the quality')
        
        # create buttons
        self.goreButtonWidget = QPushButton()
        
        # create input + output image ImageLabel
        self.previewImageLabel = ImageLabel('\n\n {0} \n\n {1}'.format("Drop image here", "Image must be square and centred"))
        
        # add sliders and button to LHS
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
        self.fundusImageSizeWidget.setRange(5,180)
        self.fundusImageSizeWidget.setSingleStep(1)
        
        self.numberOfGoresWidget.setRange(3,24)
        self.numberOfGoresWidget.setSingleStep(1)
        
        self.retinalSizeWidget.setRange(10,360)
        self.retinalSizeWidget.setSingleStep(1)
        
        self.noCutAreaWidget.setRange(0,180)
        self.noCutAreaWidget.setSingleStep(1)
        
        self.qualityWidget.setRange(10,100)
        self.qualityWidget.setSingleStep(1)
        
        # set up the spinbox
        self.rotationWidget.setSuffix("\u00b0")
        self.rotationWidget.setSingleStep(0.5)
        self.rotationWidget.setMaximum(360)
        self.rotationWidget.setMinimum(-360)
        
        # initial values
        self.fundusImageSizeWidget.setValue(self.fundusImageSizeValue)
        self.numberOfGoresWidget.setValue(self.numberOfGoresValue)
        self.retinalSizeWidget.setValue(self.retinalSizeValue)
        self.noCutAreaWidget.setValue(self.noCutAreaValue)
        self.rotationWidget.setValue(self.rotationValue)
        self.qualityWidget.setValue(self.qualityValue)

        # connect input widgets with slots
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
        
        self.qualityWidget.valueChanged.connect(self.value_changed)
        self.qualityWidget.sliderMoved.connect(self.slider_position)
        self.qualityWidget.sliderPressed.connect(self.slider_pressed)
        self.qualityWidget.sliderReleased.connect(self.slider_released)
        self.goreButtonWidget.clicked.connect(self.gore_cancel_handler)
        
        # the menubar
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('&File')
        helpMenu = menubar.addMenu('&Help')
        
        # create the icons
        openIcon = qta.icon('mdi.folder-open')
        saveIcon = qta.icon('mdi.content-save')
        saveAsIcon = qta.icon('mdi.content-save-edit')
        closeIcon = qta.icon('mdi.close')
        exitIcon = qta.icon('mdi.exit-run')
        colourIcon = qta.icon('mdi.palette')

        # the file menu actions - members so they can be updated later
        self.openAction = QAction(openIcon, '&Open input image...', self)
        self.openAction.setShortcut(QKeySequence.Open)
        self.openAction.triggered.connect(self.open_handler)
        self.saveAction = QAction(saveIcon, '&Save', self)
        self.saveAction.setShortcut(QKeySequence.Save)
        self.saveAction.triggered.connect(self.save_forwarder)
        self.saveAsAction = QAction(saveAsIcon, 'S&ave as...', self)
        self.saveAsAction.setShortcut(QKeySequence.SaveAs)
        self.saveAsAction.triggered.connect(self.save_as_forwarder)
        self.closeAction = QAction(closeIcon, '&Close', self)
        self.closeAction.setShortcut(QKeySequence.Close)
        self.closeAction.triggered.connect(self.close_handler)
        self.exitAction = QAction(exitIcon, '&Exit', self)
        self.exitAction.triggered.connect(self.exit_handler)
        self.colourAction = QAction(colourIcon, 'C&hoose background colour...', self)
        self.colourAction.triggered.connect(self.colour_dialog)
        
        # add the file menu actions
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addAction(self.closeAction)
        fileMenu.addAction(self.exitAction)
        fileMenu.addAction(self.colourAction)
        
        # the help menu actions
        self.userGuideAction = QAction('&User guide...', self)
        self.userGuideAction.triggered.connect(self.user_guide_forwarder)
        self.aboutAction = QAction('&About', self)
        self.aboutAction.triggered.connect(self.about_forwarder)
        
        # add the help menu actions
        #helpMenu.addAction(self.userGuideAction)
        helpMenu.addAction(self.aboutAction)
        
        # create toolbar and add actions
        fileToolBar = self.addToolBar("File")
        fileToolBar.addAction(self.openAction)
        fileToolBar.addAction(self.saveAction)
        fileToolBar.addAction(self.saveAsAction)
        fileToolBar.addAction(self.closeAction)
        fileToolBar.addAction(self.exitAction)
        fileToolBar.addAction(self.colourAction)

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
            return self.set_image(fileName)
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
        
    def about_dialog(self):
        msgBox = qm();
        msgBox.setText("Gore Sim Eye");
        msgBox.setInformativeText(aboutText)
        msgBox.exec();
        
    def colour_dialog(self):
        dialog = QColorDialog(self)
        dialog.setCurrentColor(self.backgroundColour)
        if dialog.exec_() == QColorDialog.Accepted:
            colour = dialog.selectedColor()
            if colour.isValid():
                self.backgroundColour = colour
    
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
            self.closeAction.setEnabled(False)
            self.aboutAction.setEnabled(False)
            self.userGuideAction.setEnabled(False)
            self.goreButtonWidget.setE
            self.goreButtonWidget.setText("")
            self.statusLabel.setText("")
        elif (self.state == State.NO_INPUT):
            self.openAction.setEnabled(True)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.closeAction.setEnabled(False)
            self.aboutAction.setEnabled(True)
            self.userGuideAction.setEnabled(True)
            self.goreButtonWidget.setEnabled(False)
            self.goreButtonWidget.setText("Gore")
            self.statusLabel.setText("No input image selected")
        elif (self.state == State.READY_TO_GORE):
            self.openAction.setEnabled(True)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.closeAction.setEnabled(True)
            self.aboutAction.setEnabled(True)
            self.userGuideAction.setEnabled(True)
            self.goreButtonWidget.setEnabled(True)
            self.goreButtonWidget.setText("Gore")
            self.statusLabel.setText("Ready to gore")
        elif (self.state == State.CALCULATING):
            self.openAction.setEnabled(False)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.closeAction.setEnabled(False)
            self.aboutAction.setEnabled(False)
            self.userGuideAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(True)
            self.goreButtonWidget.setText("Cancel")  
            self.statusLabel.setText("Calculating: Loading")  
        elif (self.state == State.CALCULATING_UNSAVED_CHANGES):
            self.openAction.setEnabled(False)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.closeAction.setEnabled(False)
            self.aboutAction.setEnabled(False)
            self.userGuideAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(True)
            self.goreButtonWidget.setText("Cancel")
            self.statusLabel.setText("Calculating: Loading")
        elif (self.state == State.CALCULATING_SAVED_CHANGES):
            self.openAction.setEnabled(False)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.closeAction.setEnabled(False)
            self.aboutAction.setEnabled(False)
            self.userGuideAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(True)
            self.goreButtonWidget.setText("Cancel") 
            self.statusLabel.setText("Calculating: Loading")     
        elif (self.state == State.CANCELLING):
            self.openAction.setEnabled(False)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.closeAction.setEnabled(False)
            self.aboutAction.setEnabled(False)
            self.userGuideAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(False)
            self.goreButtonWidget.setText("Cancelling...")
            self.statusLabel.setText("Cancelling")
        elif (self.state == State.CANCELLING_UNSAVED_CHANGES):
            self.openAction.setEnabled(False)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.closeAction.setEnabled(False)
            self.aboutAction.setEnabled(False)
            self.userGuideAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(False)
            self.goreButtonWidget.setText("Cancelling...")
            self.statusLabel.setText("Cancelling")
        elif (self.state == State.CANCELLING_SAVED_CHANGES):
            self.openAction.setEnabled(False)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.closeAction.setEnabled(False)
            self.aboutAction.setEnabled(False)
            self.userGuideAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(False)
            self.goreButtonWidget.setText("Cancelling...")
            self.statusLabel.setText("Cancelling")
        elif (self.state == State.UNSAVED_CHANGES):
            self.openAction.setEnabled(True)
            self.saveAction.setEnabled(True)
            self.saveAsAction.setEnabled(True)
            self.closeAction.setEnabled(True)
            self.aboutAction.setEnabled(True)
            self.userGuideAction.setEnabled(True)
            self.goreButtonWidget.setEnabled(True)
            self.goreButtonWidget.setText("Gore")
            self.statusLabel.setText("Unsaved changes")
        elif (self.state == State.SAVED_CHANGES):
            self.openAction.setEnabled(True)
            self.saveAction.setEnabled(True)
            self.saveAsAction.setEnabled(True)
            self.closeAction.setEnabled(True)
            self.aboutAction.setEnabled(True)
            self.userGuideAction.setEnabled(True)
            self.goreButtonWidget.setEnabled(True)
            self.goreButtonWidget.setText("Gore")
            self.statusLabel.setText("Saved changes")
        elif (self.state == State.END):
            self.openAction.setEnabled(False)
            self.saveAction.setEnabled(False)
            self.saveAsAction.setEnabled(False)
            self.closeAction.setEnabled(False)
            self.aboutAction.setEnabled(False)
            self.userGuideAction.setEnabled(False)
            self.goreButtonWidget.setEnabled(False)
            self.goreButtonWidget.setText("")
            self.statusLabel.setText("End")
        else:
            # invalid state: do nothing
            pass
        
    def open_handler(self, filePath = None):
        # open handler: called with filePath from drag and drop 
        if (self.state == State.NO_INPUT or
            self.state == State.READY_TO_GORE or
            self.state == State.SAVED_CHANGES):
            success = False
            if (filePath  and self.set_image(filePath)):
                success == True
            elif (self.open_image_dialog()):
                success = True
            if (success):
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
            if (filePath):
                # called from drag and drop: allowed but does nothing...
                self.transition()
            else:
                #... otherwise we shouldn't be here
                self.raise_state_exception()
        elif (self.state == State.UNSAVED_CHANGES):
            ret = qm.question(self,'', "Unsaved changes: open new image and lose changes?", qm.Yes | qm.No)
            if (ret == qm.Yes):
                success = False
                if (filePath and self.set_image(filePath)):
                    success == True
                elif (self.open_image_dialog()):
                    success = True
                if (success):
                    self.outputPath = None
                    self.transition(State.READY_TO_GORE)
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
        
    def close_handler(self):
        if (self.state == State.NO_INPUT or
            self.state == State.CALCULATING or
            self.state == State.CALCULATING_SAVED_CHANGES or
            self.state == State.CALCULATING_UNSAVED_CHANGES or
            self.state == State.CANCELLING or
            self.state == State.CANCELLING_SAVED_CHANGES or
            self.state == State.CANCELLING_UNSAVED_CHANGES or
            self.state == State.START or
            self.state == State.END):
            self.raise_state_exception()
        elif (self.state == State.READY_TO_GORE or
              self.state == State.SAVED_CHANGES):
            self.clear_image()
            self.transition(State.NO_INPUT)
        elif (self.state == State.UNSAVED_CHANGES):
            ret = qm.question(self, '', "Unsaved changes: close and lose changes?", qm.Yes | qm.No)
            if (ret == qm.Yes):
                self.clear_image()
                self.transition(State.NO_INPUT)
            else:
                self.transition()
        else:
            # invalid state
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
        elif (self.state == State.READY_TO_GORE):
            self.transition(State.CALCULATING)
            self.start_calculating()
        elif (self.state == State.UNSAVED_CHANGES):
            self.transition(State.CALCULATING_UNSAVED_CHANGES)
            self.start_calculating()
        elif (self.state == State.SAVED_CHANGES):
            self.transition(State.CALCULATING_SAVED_CHANGES)
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
            
    def progress_handler(self, i):
        logging.debug ("Calculation progress: {0}".format(i))
        if (i == 0):
            self.statusLabel.setText("Calculating: Getting eye coordinates")
        elif (i == 1):
            self.statusLabel.setText("Calculating: Rotating projection")
        elif (i == 2):
            self.statusLabel.setText("Calculating: Projecting")
        elif (i == 3):
            self.statusLabel.setText("Calculating: Projecting at pole")
            
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
        
    def about_forwarder(self):
        self.help_handler(False)
        
    def user_guide_forwarder(self):
        self.help_handler(True)
        
    def help_handler(self, userGuide = False):
        if (self.state == State.START or
            self.state == State.CALCULATING or
            self.state == State.CALCULATING_UNSAVED_CHANGES or
            self.state == State.CALCULATING_SAVED_CHANGES or
            self.state == State.CANCELLING or
            self.state == State.CANCELLING_UNSAVED_CHANGES or
            self.state == State.CANCELLING_SAVED_CHANGES or
            self.state == State.END):
            self.raise_state_exception()
        elif (self.state == State.NO_INPUT or
              self.state == State.READY_TO_GORE or
              self.state == State.UNSAVED_CHANGES or
              self.state == State.SAVED_CHANGES):
            if (userGuide):
                self.browser.show()
            else: # about
                self.about_dialog()
                
            self.transition()
        else:
            # invalid state
            self.raise_state_exception()
            
        self.update_widgets()
            
    def value_changed(self, i):
        # handle updates from the ui elements (sliders)
        if (self.sender() == self.fundusImageSizeWidget):
            self.fundusImageSizeValue = i
        elif (self.sender() == self.numberOfGoresWidget):
            self.numberOfGoresValue = i
        elif (self.sender() == self.retinalSizeWidget):
            self.retinalSizeValue = i
        elif (self.sender() == self.noCutAreaWidget):
            self.noCutAreaValue = i
        elif (self.sender() == self.rotationWidget):
            self.rotationValue = i
        elif (self.sender() == self.qualityWidget):
            self.qualityValue = i
            
        self.update_inputs_text()
            
    def update_inputs_text(self):
        self.fundusImageSizeLabel.setText("Image extent: {0}\u00b0".format(self.fundusImageSizeValue))
        self.numberOfGoresLabel.setText("Number of Gores: {0}".format(self.numberOfGoresValue))
        self.retinalSizeLabel.setText("Retinal size: {0}\u00b0".format(self.retinalSizeValue))
        self.noCutAreaLabel.setText("No-cut area: {0}\u00b0".format(self.noCutAreaValue))
        self.rotationLabel.setText("Rotation:")
        self.qualityLabel.setText("Quality: {0}%".format(self.qualityValue))

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
            self.open_handler(file_path)

            event.accept()
        else:
            event.ignore()

    def set_image(self, file_path):
        self.imagePath = file_path
        self.previewImageLabel.setPixmap(QPixmap(file_path))
        return True # todo return success
    
    def clear_image(self):
        self.imagePath = None
        self.previewImageLabel.clearPixmap()
        
    def get_inputs(self):
        # collect the inputs to the calculation as a dict
        inputs = dict(image_path = self.imagePath, 
                      focal_length = 24, 
                      alpha_max = deg2rad(self.fundusImageSizeValue / 2), # account for difference in angle measurement in gore2 
                      num_gores = self.numberOfGoresValue, 
                      alpha_limit = deg2rad(self.retinalSizeValue / 2), # account for difference in angle measurement in gore2
                      phi_no_cut = deg2rad(self.noCutAreaValue / 2), # account for difference in angle measurement in gore2
                      rotation = self.rotationValue,
                      quality = self.qualityValue,
                      background_colour = self.backgroundColour.getRgb()
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
        self.worker.progress.connect(self.progress_handler)
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
        import gore2
        gore2.signal = self.progress
        tic = perf_counter()
        im = gore2.make_rotary_adjusted(**self.inputs)
        toc = perf_counter()
        time = toc - tic
        if (im == None):
            logging.debug("Calculation CANCELLED after {0:4f}".format(time))
            self.complete = False
        else:
            logging.debug("Calculation COMPLETED in {0:.4f}s".format(time) )
            qim = ImageQt(im)
            pix = QPixmap.fromImage(qim)
            logging.debug("Returned image has size {0}px x {1}px".format(pix.width(), pix.height()))
            self.outputPixmap = pix
        
        self.finished.emit()

def main():
    app = QApplication(sys.argv)
    pixmap = QPixmap("splash.png")
    splash = QSplashScreen(pixmap)
    
    # show the splash screen first...
    splash.show()
    app.processEvents()
    loadingString = "loading..."
    splash.showMessage(loadingString)
    
    loadingString += ("ready")
    splash.showMessage(loadingString)
    
    window = MainWindow()
    # close the splash screen after waiting 1s (in addition to load time)
    QTimer.singleShot(1000, lambda: splash.finish(window))
    window.resize(600,400)
    window.show()
    
    sys.exit( app.exec_() )
    
if __name__ == "__main__":
    main()