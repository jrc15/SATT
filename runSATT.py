from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtCore import QRunnable, Qt, QThreadPool, pyqtSlot

from balsam_main import Ui_Dialog, Receiver
from model import Model

import glob
import sys
import os


class WorkerSignals(QObject):

    progress = pyqtSignal(int)
    finished = pyqtSignal()
    

# Create a worker class
class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        self.fn(*self.args, **self.kwargs)


class DialogUIClass( Ui_Dialog ):
    def __init__( self ):
        '''Initialize the super class
        '''
        print("Dialog_Ui class intiated")
        super().__init__()
        #self.model = Model()
        self.signals = WorkerSignals()

        # Thread runner
        self.threadpool = QThreadPool()

    # slot
    def loadFolderSlot( self ):
        ''' Called when the user presses the load folder button
        '''
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        folderName = QtWidgets.QFileDialog.getExistingDirectory()
        if folderName:
            self.inputFolderLineEdit.setText(folderName)

    # slot
    def loadOutputSlot( self ):
        ''' Called when the user presses the load Output button
        '''
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        outputName = QtWidgets.QFileDialog.getExistingDirectory()
        if outputName:
            self.outputFolderLineEdit.setText(outputName)

    # slot
    def loadOutPathSlot( self ):
        ''' Called when the user presses the load OutPath button
        '''
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        outPathName = QtWidgets.QFileDialog.getExistingDirectory()
        if outPathName:
            self.outpathLineEdit.setText(outPathName)

    # slot
    def runExractMapSlot( self ):
               
        # pull data from recieve recieve variable
        print('data collected from reciever class: ', Receiver.share)
        results = Receiver.share
        
        signals = WorkerSignals()
    
        dirPath = str(self.inputFolderLineEdit.text())
        flwDir = str(self.outputFolderLineEdit.text())
        outPath = str(self.outpathLineEdit.text())
        imageCount = len(glob.glob(dirPath + '\*.JPG'))
        
        gen = Model.extractBalsam(self, dirPath, flwDir, outPath, results)
        for n in range(imageCount+1):
            try:
                value = next(gen)
                self.signals.progress.emit(value)

            except:
                self.signals.finished.emit()

    def run_worker(self):  
        self.restart()    

        # Pass the function to execute
        self.worker = Worker(self.runExractMapSlot) # Any other args, kwargs are passed to the run function
        self.signals.progress.connect(self.updateProgressBar)
        self.threadpool.start(self.worker)

        # Connect the worker signals to the message box
        self.signals.finished.connect(self.show_message_box)

    def show_message_box(self):
        QtWidgets.QMessageBox.information(None, "Processing complete", "The software has finished processing.")

    def updateProgressBar(self, val):
        self.extractionBar.setValue(val)

    def restart(self):
        self.extractionBar.setValue(0)



def main():
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QMainWindow()
    ui = DialogUIClass()
    ui.setupUi(Dialog)
    Dialog.show()  
    sys.exit(app.exec_())

main()
