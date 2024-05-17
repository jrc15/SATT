# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import QDialog, QWidget, QApplication

import os
import sys
import pyqtgraph as pg
from PIL import Image

# pyinstaller loses path to these libraries
#import numpy.random.common
#import numpy.random.bounded_integers
#import numpy.random.entropy

from numpy import asarray

from model import Model

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

# change style fo application
app = QApplication(sys.argv)
app.setStyle('Fusion')

# change default font across application
font = QtGui.QFont("Calibri") # "Georgia")
QApplication.setFont(font)


class Receiver:
    share = [115, 10, 0, 230, 200, 0, 'Ellipse', 15, 15, 43, (0, 255, 0)]
        
    def update(self, value, cls):
        cls.share = value
        #print('new share value: ', cls.share) 
        
    def __init__(self, results):
        print(type(results))
        #print(f'Received results: ', results)
        
        self.results = results
        self.update(results, Receiver)



class MySlider(QWidget):
    def __init__(self, name, maxi, mini, font_size, orientation, setValue, parent=None):
        super(MySlider, self).__init__(parent)

        self.label = QtWidgets.QLabel(name, self)
        self.label.setFont(QtGui.QFont("Sanserif", font_size))
        self.slider = QtWidgets.QSlider(orientation, objectName=name)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.setMaximum(maxi)
        self.slider.setMinimum(mini)
        self.slider.setTickInterval(10)
        self.slider.setValue(setValue)

        self.numbox = QtWidgets.QSpinBox(objectName="spinBox_" + name)
        self.numbox.setRange(self.slider.minimum(), self.slider.maximum())
        self.numbox.setValue(setValue)
        
        self.numbox.valueChanged.connect(self.slider.setValue)
        self.slider.valueChanged.connect(self.numbox.setValue)
        
        # set layout and widget
        self.horizontalLayout_slider = QtWidgets.QHBoxLayout(self, objectName="layoutH_"+name)
        self.horizontalLayout_slider.addWidget(self.label)
        self.horizontalLayout_slider.addWidget(self.slider)
        self.horizontalLayout_slider.addWidget(self.numbox)


class Advanced_Popup(QDialog):

    #####################################################################################
            
    ### To Do ###
    
    #    
    
    # - Completed #### Flower Shape if 1 check bx checked, decheck other checkboxes 
    # - Completed #### Make Labels Bold and larger text 
    # - Completed #### Add previous button to Threshold detection widget 
    # - Completed #### Send advance window data parameter values to model functionality
    # - Completed #### Connect functionality to each step
    # - Completed #### Added popup to show completed processing. 
    # - Completed #### Load first image in folder to graphics view
    # - Completed #### Plot images as numpy arrays to provide axis of pixel ranges. Replaced graphics view with pyqtgraph and plotted image as np.array.
    # - Completed #### update next and previous functions if they are the last one in the list to reset from begining or end ect. 
    # - Completed #### added text to line edits on mainwindow. 
    # - Completed #### connect process button to update image array based on user inputs. 
    # - Completed #### add a image reset 
    # - Completed #### connect buttons to funcitonality. 
    # - Completed #### change style of application to modern style - fusion. 
    # - Completed #### changed defualt font to easier to read style - Calibri
    # - Completed #### changed header font style to have underline set true, to help distinguish items
    # - Completed #### modified button layout on advanced popup for easier viewing and use. 
    
    ######################################################################################


    def __init__(self):
        super().__init__()

        self.setWindowTitle("Advanced Software Settings...")
        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        w = sizeObject.width()*0.8 #height()
        
        # set fonts
        headerFont = QtGui.QFont("Arial", pointSize=13, weight=QtGui.QFont.Bold)
        headerFont.setUnderline(True)
        self.hsvLabel = QtWidgets.QLabel("Detection HSV Threholds")
        self.shpLabel = QtWidgets.QLabel("Flower Shape")
        self.sizeLabel = QtWidgets.QLabel("Flower Size")
        self.objectLabel = QtWidgets.QLabel("Object Height")
        self.bboxLabel = QtWidgets.QLabel("Bounding Box colour")
        
        self.hsvLabel.setFont(headerFont)
        self.shpLabel.setFont(headerFont)
        self.sizeLabel.setFont(headerFont)
        self.objectLabel.setFont(headerFont)
        self.bboxLabel.setFont(headerFont)
        
        # widget 1 - input line edit
        self.inCalLabel = QtWidgets.QLabel("Select input folder", objectName="inCalLabel")
        self.inCalFolderLineEdit = QtWidgets.QLineEdit(self, objectName="inCalFolderLineEdit")
        self.inCalFolderButton = QtWidgets.QPushButton(self, objectName="inCalFolderButton")
        
        # widget 2 - Threshold sliders
            # Threshold slider1 - Hue For HSV, 
                # the hue range is [0,179], 
                # the saturation range is [0,255],
                # the value range is [0,255].
        self.sliderHL = MySlider("Lower_H", 255, 0, 10, QtCore.Qt.Horizontal, 115, self)
        self.sliderSL = MySlider("Lower_S", 255, 0, 10, QtCore.Qt.Horizontal, 10, self)
        self.sliderVL = MySlider("Lower_V", 255, 0, 10, QtCore.Qt.Horizontal, 0, self)

        self.sliderHU = MySlider("Upper_H", 255, 0, 10, QtCore.Qt.Horizontal, 230, self)
        self.sliderSU = MySlider("Upper_S", 255, 0, 10, QtCore.Qt.Horizontal, 200, self)
        self.sliderVU = MySlider("Upper_V", 255, 0, 10, QtCore.Qt.Horizontal, 0, self)
        
            # # widget & layout
        self.layoutWidget_slider1 = QtWidgets.QWidget(objectName="layoutWidget_slider1")
        self.horizontalLayout_slider1 = QtWidgets.QGridLayout(self.layoutWidget_slider1)
        self.horizontalLayout_slider1.addWidget(self.sliderHL, 0,0,1,3)
        self.horizontalLayout_slider1.addWidget(self.sliderSL, 1,0,1,3)
        self.horizontalLayout_slider1.addWidget(self.sliderVL, 2,0,1,3)
        self.horizontalLayout_slider1.addWidget(QtWidgets.QLabel("  "), 3,0,1,3)
        self.horizontalLayout_slider1.addWidget(self.sliderHU, 4,0,1,3)
        self.horizontalLayout_slider1.addWidget(self.sliderSU, 5,0,1,3)
        self.horizontalLayout_slider1.addWidget(self.sliderVU, 6,0,1,3)
        self.layoutWidget_slider1.setContentsMargins(0,0,0,0)
        
        # widget 3 - threshold buttons
        # Click Advance Button
        self.resetButton = QtWidgets.QPushButton(objectName="ResetButton")
        self.processButton = QtWidgets.QPushButton(objectName="ProcessButton")
        self.previousButton = QtWidgets.QPushButton(objectName="PreviousButton")
        self.nextButton = QtWidgets.QPushButton(objectName="NextButton")
        self.finishButton = QtWidgets.QPushButton(objectName="FinishButton")
        
        # widget 4 - elipsoid search
               # # Checkbox
        self.checkEllBox = QtWidgets.QCheckBox("Ellipse", objectName="EllCheckBox", checked=True)
        self.checkCroBox = QtWidgets.QCheckBox("Cross", objectName="CroCheckBox", checked=False)
        self.checkRecBox = QtWidgets.QCheckBox("Rectangle", objectName="RecCheckBox", checked=False)
        self.checkEllBox.setEnabled(True)
        
        # widget 5 - object size search line edits
        self.numboxX = QtWidgets.QSpinBox(value=15, objectName="Flower_Size_X")
        self.numboxX.setRange(0,50000)
        self.numboxY = QtWidgets.QSpinBox(value=15, objectName="Flower_Size_Y")
        self.numboxY.setRange(0,50000)
        
        # widget 7 - real object height & bbounding box colour
        self.numboxOs = QtWidgets.QSpinBox(value=43, objectName="Object_Height_Y")
        self.numboxOs.setRange(0,1000)
        self.checkRedBox = QtWidgets.QCheckBox("Red", objectName="RedCheckBox", checked=False)
        self.checkGreenBox = QtWidgets.QCheckBox("Green", objectName="GreenCheckBox", checked=True)
        self.checkBlueBox = QtWidgets.QCheckBox("Blue", objectName="BlueCheckBox", checked=False)
        self.checkGreenBox.setEnabled(True)
        
        # widget 6 - graphics view
        #self.imageView = QtWidgets.QGraphicsView(objectName="graphicsView")
        self.plot = pg.PlotItem()
        self.plot.setLabel(axis='left', text='Y-Pixel Size')
        self.plot.setLabel(axis='bottom', text='X-Pixel Size')
        
        self.imageView = pg.ImageView(view=self.plot)
        self.imageView.ui.histogram.hide()               # hide histogram
        self.imageView.ui.roiBtn.hide()             # hide ROI button
        self.imageView.ui.menuBtn.hide()              # hide normalise button
        self.imageView.setFixedWidth(w*0.6)

        
        # merge in left Layout
        leftAdvancedLayout = QtWidgets.QGridLayout()   # left subparent widget
        
        #layout.addWidget(widget, row, column, rowSpan, columnSpan, alignment)
        leftAdvancedLayout.addWidget(self.inCalLabel, 0,0,1,1) 
        leftAdvancedLayout.addWidget(self.inCalFolderLineEdit, 0,1,1,2)
        leftAdvancedLayout.addWidget(self.inCalFolderButton, 0,3,1,1)
        
        leftAdvancedLayout.addWidget(QtWidgets.QLabel("  "), 1,1)
        leftAdvancedLayout.addWidget(self.hsvLabel, 2,0,1,4)
        leftAdvancedLayout.addWidget(self.layoutWidget_slider1, 3,0,1,4)

        leftAdvancedLayout.addWidget(self.resetButton, 4,1)
        leftAdvancedLayout.addWidget(self.processButton, 4,2)

        leftAdvancedLayout.addWidget(QtWidgets.QLabel("  "), 5,1)
        leftAdvancedLayout.addWidget(self.shpLabel, 6,0,1,4)        
        leftAdvancedLayout.addWidget(self.checkEllBox, 7,0)
        leftAdvancedLayout.addWidget(self.checkCroBox, 7,1)
        leftAdvancedLayout.addWidget(self.checkRecBox, 7,2)
        
        leftAdvancedLayout.addWidget(QtWidgets.QLabel("  "), 8,1)
        leftAdvancedLayout.addWidget(self.sizeLabel, 9,0,1,4)  
        leftAdvancedLayout.addWidget(QtWidgets.QLabel("Pixel Size Range (X,Y):"), 10,0)
        leftAdvancedLayout.addWidget(self.numboxX, 10,1)
        leftAdvancedLayout.addWidget(self.numboxY, 10,2)
        
        leftAdvancedLayout.addWidget(QtWidgets.QLabel("  "), 11,1)
        leftAdvancedLayout.addWidget(self.objectLabel, 12,0,1,4)  
        leftAdvancedLayout.addWidget(QtWidgets.QLabel("Real Object Height (Y):"), 13,0)
        leftAdvancedLayout.addWidget(self.numboxOs, 13,1)
        
        leftAdvancedLayout.addWidget(QtWidgets.QLabel("  "), 14,1)
        leftAdvancedLayout.addWidget(self.bboxLabel, 15,0,1,4)  
        leftAdvancedLayout.addWidget(self.checkRedBox, 16,0)
        leftAdvancedLayout.addWidget(self.checkGreenBox, 16,1)
        leftAdvancedLayout.addWidget(self.checkBlueBox, 16,2)
        
        leftAdvancedLayout.addWidget(QtWidgets.QLabel("  "), 17,1)
        leftAdvancedLayout.addWidget(self.previousButton, 18,1)
        leftAdvancedLayout.addWidget(self.nextButton, 18,2)
        leftAdvancedLayout.addWidget(self.finishButton, 19,1,1,2)
        
        self.widgetLeft = QtWidgets.QWidget()
        self.widgetLeft.setLayout(leftAdvancedLayout)
        self.widgetLeft.setFixedWidth(int(w*0.5))
        
        # merge all widgets in parent widget
        parentAdvancedLayout = QtWidgets.QHBoxLayout() # parent widget 
        parentAdvancedLayout.addWidget(self.widgetLeft)
        parentAdvancedLayout.addWidget(self.imageView)
        
        self.setLayout(parentAdvancedLayout)


        # Add Functionality to Buttons
        self.retranslateUi(self)
        
        self.checkEllBox.clicked.connect(self.toggle)
        self.checkCroBox.clicked.connect(self.toggle)
        self.checkRecBox.clicked.connect(self.toggle)
        
        self.checkRedBox.clicked.connect(self.toggle)
        self.checkGreenBox.clicked.connect(self.toggle)
        self.checkBlueBox.clicked.connect(self.toggle)
        
        self.resetButton.clicked.connect(self.resetImage)
        self.processButton.clicked.connect(self.processImage)
        self.finishButton.clicked.connect(self.sendData)# needs to send to a holding cell for changed values
        self.inCalFolderButton.clicked.connect(self.loadImageSlot)
        self.nextButton.clicked.connect(self.nextImage)
        self.previousButton.clicked.connect(self.previousImage)

        QtCore.QMetaObject.connectSlotsByName(self) 

    def retranslateUi(self, Advanced):
        _translate = QtCore.QCoreApplication.translate
        Advanced.setWindowTitle(_translate("Advanced", "Advanced Software Settings..."))
        self.inCalLabel.setText(_translate("Advanced", "Select input folder"))
        self.inCalFolderButton.setText(_translate("Advanced", "..."))
        self.processButton.setText(_translate("Advanced", "Process Image"))
        self.previousButton.setText(_translate("Advanced", "Previous Image"))
        self.nextButton.setText(_translate("Advanced", "Next Image"))
        self.finishButton.setText(_translate("Advanced", "Finish"))
        self.resetButton.setText(_translate("Advanced", "Reset Image"))
        self.inCalFolderLineEdit.setText(_translate("Dialog", "path to file ..."))
    
    def toggle(self):
        ''' when check box is checked, uncheck others'''
        # get name of checked box
        sender_name = self.sender().objectName()
        #print(f"The name of the connected slot is {sender_name}")
        
        if sender_name == "EllCheckBox":
            self.checkCroBox.setChecked(False)
            self.checkRecBox.setChecked(False)
        elif sender_name == "CroCheckBox":
            self.checkEllBox.setChecked(False)
            self.checkRecBox.setChecked(False)
        elif sender_name == "RecCheckBox":
            self.checkEllBox.setChecked(False)
            self.checkCroBox.setChecked(False)
            
        elif sender_name == "RedCheckBox":
            self.checkGreenBox.setChecked(False)
            self.checkBlueBox.setChecked(False)
        elif sender_name == "GreenCheckBox":
            self.checkRedBox.setChecked(False)
            self.checkBlueBox.setChecked(False)
        elif sender_name == "BlueCheckBox":
            self.checkGreenBox.setChecked(False)
            self.checkRedBox.setChecked(False)

    def collectVars(self):
        ''' collect variables from advanced window for use in main functionality'''
        
        Lh = self.findChild(QtWidgets.QSpinBox, "spinBox_Lower_H").value()        # Lower H
        Ls = self.findChild(QtWidgets.QSpinBox, "spinBox_Lower_S").value()        # Lower S
        Lv = self.findChild(QtWidgets.QSpinBox, "spinBox_Lower_V").value()        # Lower V
        Uh = self.findChild(QtWidgets.QSpinBox, "spinBox_Upper_H").value()        # Upper H
        Us = self.findChild(QtWidgets.QSpinBox, "spinBox_Upper_S").value()        # Upper S
        Uv = self.findChild(QtWidgets.QSpinBox, "spinBox_Upper_V").value()        # Upper V

        # Flower Shape - Return Checked Box Value
        if self.checkEllBox.isChecked():
            Fshp = "Ellipse"
        elif self.checkCroBox.isChecked:
            Fshp = "Cross"
        elif self.checkRecBox.isChecked:
            Fshp = "Rectangle"
            
        # Flower Size X, Y
        Fx = self.findChild(QtWidgets.QSpinBox, "Flower_Size_X").value()        # Flower_Size_X
        Fy = self.findChild(QtWidgets.QSpinBox, "Flower_Size_Y").value()        # Flower_Size_Y

        # Object Size (mm)
        Os = self.findChild(QtWidgets.QSpinBox, "Object_Height_Y").value()      # Real Object Height
        
        # Bounding Box Colour - Return Checked Box Value - (b,g,r)
        if self.checkRedBox.isChecked():
            Bbox = (0,0,255)
        elif self.checkBlueBox.isChecked:
            Bbox = (255,0,0)
        elif self.checkGreenBox.isChecked:
            Bbox = (0,255,0)

        values = [Lh, Ls, Lv, Uh, Us, Uv, Fshp, Fx, Fy, Os, Bbox]
        
        return values

    def sendData(self):
        values = self.collectVars()        # collect values from window
        Receiver(values)                   # send values to new store class
        self.close()                       # close window

    def refreshAll( self ):
        "Updates the widgets whenever an interaction happens."
        
        # refresh graphics viewer 1
        self.imageView.hide()
        self.imageView.show()

    def checkPath(self, image_path):
        if os.path.isfile(image_path):            
            image = Image.open(image_path) # open image
            numpydata = asarray(image)     # conver timage to array
            img = pg.ImageItem(numpydata)  # read array as image item
            img.rotate(90)                 # rotate image
            self.imageView.ui.graphicsView.setCentralItem(self.plot)
            self.plot.addItem(img)           # add image item to graphics layout 
            self.plot.autoRange()            # adjust ranges to fit image. 

            self.refreshAll()

    def loadImageSlot( self ):
        ''' Called when the user presses the load file button
        '''
        
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
                        None,
                        "QFileDialog.getOpenFileName()",
                        "",
                        "All Files (*);;Python Files (*.py)",
                        options=options)
        if fileName:
            self.checkPath(fileName)
            self.inCalFolderLineEdit.setText(fileName)
#            self.refreshAll()

            dirpath = os.path.dirname(fileName)
            self.fileList = []
            self.current_index = 0
            for f in os.listdir(dirpath):
                fpath = os.path.join(dirpath, f)
                if os.path.isfile(fpath) and f.endswith(('.png', '.jpg', '.jpeg', '.JPG', '.JPEG')):
                    self.fileList.append(fpath)

            try:
                self.fileList.sort(key=lambda f: int(re.sub('\D', '', f)))

            except:
                self.fileList.sort()
                print(self.fileList)

    def nextImage(self):
        self.current_index += 1

        # ensure that the file list has not been cleared due to missing files
        if self.fileList:
            try:
                filename = self.fileList[self.current_index]
                print(filename)
                self.inCalFolderLineEdit.setText(filename)
                self.checkPath(filename)

            except:
                # the iterator has finished, restart it
                print('restarting index')
                self.current_index = -1     # has to be -1 due to first line of this function ^
                self.nextImage()

    def previousImage(self):
        self.current_index -= 1
        print(self.current_index)

        # ensure that the file list has not been cleared due to missing files
        if self.fileList:
            try:
                filename = self.fileList[self.current_index]
                print(filename)
                self.inCalFolderLineEdit.setText(filename)
                self.checkPath(filename)

            except:
                # the iterator has finished, restart it
                self.current_index = 0
                self.previousImage()

    def processImage(self):
        # process current image in text edit
        image = str(self.inCalFolderLineEdit.text())
        # collect values from advanced window
        results = self.collectVars()        # collect values from window
        # run through model function
        mask = Model.processAdvance( self, image, results)
        # convert mask image to np.array
        numpydata = asarray(mask)     # convert image to array
        # load processed image to plot
        img = pg.ImageItem(numpydata)  # read array as image item
        img.rotate(90)                 # rotate image
        self.plot.addItem(img)           # add image item to graphics layout 
        self.plot.autoRange()            # adjust ranges to fit image. 
    
    def resetImage(self):
        # process current image in text edit
        image = str(self.inCalFolderLineEdit.text())
        self.checkPath(image)



class Ui_Dialog(QObject):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        self.centralwidget = QtWidgets.QWidget(Dialog)
        self.centralwidget.setObjectName("centralwidget")
        
        # set Window Icon
        #self.centralwidget.setWindowIcon(QtGui.QIcon('./Icon-DetectedBalsam.ico'))

        # Balsam Image Label
        self.imageLabel = QtWidgets.QLabel(Dialog)
        self.imageLabel.setObjectName("imageLabel")
        pixmap = QtGui.QPixmap('C:/Users/Jack/OneDrive - Aberystwyth University/PhD/Chapters/Chapter2-Balsam/app/DetectedBalsam.png') 
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setFrameShape(QtWidgets.QFrame.Panel)
        self.imageLabel.setLineWidth(1)

        # Function Button
        self.extractMapButton = QtWidgets.QPushButton(Dialog)
        self.extractMapButton.setCheckable(False)
        self.extractMapButton.setObjectName("extractMapButton")

        # Checkbox
        self.checkCNNBox = QtWidgets.QCheckBox(Dialog)
        self.checkCNNBox.setChecked(False)
        self.checkCNNBox.setObjectName("checkCNNBox")

        # Input Folder Button
        self.inputLabel = QtWidgets.QLabel(Dialog)
        self.inputLabel.setObjectName("inputLabel")
        self.inputFolderLineEdit = QtWidgets.QLineEdit(Dialog)
        self.inputFolderLineEdit.setObjectName("inputFolderLineEdit")
        self.inputFolderButton = QtWidgets.QPushButton(Dialog)
        self.inputFolderButton.setObjectName("inputFolderButton")

        # Output Folder Button
        self.outputLabel = QtWidgets.QLabel(Dialog)
        self.outputLabel.setObjectName("outputLabel")
        self.outputFolderLineEdit = QtWidgets.QLineEdit(Dialog)
        self.outputFolderLineEdit.setObjectName("outputFolderLineEdit")
        self.outputFolderButton = QtWidgets.QPushButton(Dialog)
        self.outputFolderButton.setObjectName("outputFolderButton")

        # Outpath Folder Button
        self.outpathLabel = QtWidgets.QLabel(Dialog)
        self.outpathLabel.setObjectName("outpathLabel")
        self.outpathLineEdit = QtWidgets.QLineEdit(Dialog)
        self.outpathLineEdit.setObjectName("outpathLineEdit")
        self.outpathButton = QtWidgets.QPushButton(Dialog)
        self.outpathButton.setObjectName("outpathButton")

        # Balsam Extraction Progress Bar
        self.extractionLabel = QtWidgets.QLabel(Dialog)
        self.extractionLabel.setObjectName("extractionLabel")
        self.extractionBar = QtWidgets.QProgressBar(Dialog)
        self.extractionBar.setObjectName("extractionBar")
        self.extractionBar.setValue(0)

        # Click Advance Button
        self.advButton = QtWidgets.QPushButton()
        self.advButton.setObjectName("advButton")
        
        #### layouts  ####
        parentLayout = QtWidgets.QGridLayout() # parent widget 
                   
        # merge in QVbox Layout
        parentLayout.addWidget(self.inputLabel, 0,0)
        parentLayout.addWidget(self.inputFolderLineEdit, 0,1)
        parentLayout.addWidget(self.inputFolderButton, 0,2)
        
        parentLayout.addWidget(self.outputLabel, 1,0)
        parentLayout.addWidget(self.outputFolderLineEdit,1,1)
        parentLayout.addWidget(self.outputFolderButton,1,2)
        
        parentLayout.addWidget(self.outpathLabel, 2,0)
        parentLayout.addWidget(self.outpathLineEdit, 2,1) #
        parentLayout.addWidget(self.outpathButton, 2,2)
        
        # extract button & checkbox
        btnLayout = QtWidgets.QHBoxLayout()
        btnLayout.addWidget(self.extractMapButton)
        btnLayout.addWidget(self.checkCNNBox)
        self.btnWidget = QtWidgets.QWidget(self.centralwidget)
        self.btnWidget.setLayout(btnLayout)
        
        parentLayout.addWidget(self.btnWidget, 3,1)
        
        parentLayout.addWidget(self.imageLabel, 4, 1)#, 1, 3)
        
        parentLayout.addWidget(self.extractionLabel, 5,0)
        parentLayout.addWidget(self.extractionBar, 5,1)#,1,2)
        parentLayout.addWidget(self.advButton, 5,2)
        
        self.parentWidget = QtWidgets.QWidget(self.centralwidget)
        self.parentWidget.setLayout(parentLayout)
        
        # Resize dialog to tab size   
        Dialog.setCentralWidget(self.parentWidget)

        # Add Functionality to Buttons
        self.retranslateUi(Dialog)
        self.inputFolderButton.clicked.connect(self.loadFolderSlot)
        self.outputFolderButton.clicked.connect(self.loadOutputSlot)
        self.extractMapButton.clicked.connect(self.run_worker)
        self.outpathButton.clicked.connect(self.loadOutPathSlot)
        self.advButton.clicked.connect(self.open_Advanced)        
        QtCore.QMetaObject.connectSlotsByName(Dialog)       


    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Extract & Map Software"))
        self.extractMapButton.setText(_translate("Dialog", "Extract and Map"))
        self.checkCNNBox.setText(_translate("Dialog", "Only CNN training"))
        self.inputLabel.setText(_translate("Dialog", "Select input folder"))
        self.inputFolderButton.setText(_translate("Dialog", "..."))
        self.inputFolderLineEdit.setText(_translate("Dialog", "path to image folder ..."))
        self.outputLabel.setText(_translate("Dialog", "Select flowers folder"))
        self.outputFolderButton.setText(_translate("Dialog", "..."))
        self.outputFolderLineEdit.setText(_translate("Dialog", "path to output processed image folder ..."))
        self.outpathLabel.setText(_translate("Dialog", "Select vector path"))
        self.outpathButton.setText(_translate("Dialog", "..."))
        self.outpathLineEdit.setText(_translate("Dialog", "path to output vector folder ..."))
        self.extractionLabel.setText(_translate("Dialog", "Extraction Progress:"))
        self.advButton.setText(_translate("Dialog", "Advanced..."))
        

    def open_Advanced(self, s):
        
        dlg = Advanced_Popup()
        if dlg.exec():
            print("Success!")
        else:
            print("Closed!")


    @pyqtSlot( )
    def loadFolderSlot( self ):
        pass

    @pyqtSlot( )
    def loadOutputSlot( self ):
        pass

    @pyqtSlot( )
    def runExractMapSlot( self ):
        pass

    @pyqtSlot( )
    def loadOutPathSlot( self ):
        pass

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    receiver = Receiver()
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
