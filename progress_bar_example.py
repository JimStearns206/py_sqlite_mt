"""
From http://stackoverflow.com/questions/8007602/looping-qprogressbar-gives-error-qobjectinstalleventfilter-cannot-filter-e
"""
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import (QApplication, QDialog, QProgressBar)
import sys, time

class BusyBar(QThread):                     # Looping progress bar
    # create the signal that the thread will emit
    changeValue = pyqtSignal(int)
    def __init__(self, text = "" ):
        QThread.__init__(self)
        self.text = text
        self.stop = False
        self.proBar = QProgressBar()
        self.proBar.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen )
        self.proBar.setRange( 0, 100 )
        self.proBar.setTextVisible( True )
        self.proBar.setFormat( self.text )
        self.proBar.setValue( 0 )
        self.proBar.setFixedSize( 500 , 50 )
        self.proBar.setAlignment(Qt.AlignCenter)
        self.proBar.show()

        self.changeValue.connect(self.proBar.setValue, Qt.QueuedConnection)
        # Make the Busybar delete itself and the QProgressBar when done
        self.finished.connect(self.onFinished)

    def run( self ):
        while not self.stop:                # keep looping while self is visible
            # Loop sending mail
            for i in range(100):
                # emit the signal instead of calling setValue
                # also we can't read the progress bar value from the thread
                self.changeValue.emit( i )
                time.sleep(0.05)
            self.changeValue.emit( 0 )

    def onFinished(self):
        self.proBar.deleteLater()
        self.deleteLater()

    def Kill(self):
        self.stop = True

class LayoutCreator(QDialog):
    def __init__(self , parent=None):
        super(LayoutCreator, self).__init__(parent)
        self.Cameras_Update()

    def Cameras_Update( self ):
        # Looping progress bar
        self.busyBar = BusyBar( text = "Gathering Camera Data" )
        self.busyBar.start()

        # loop through folder structure storing data

        # Simulate async activity that doesn't block the GUI event loop
        # (if you do everything without giving control back to
        # the event loop, you have to call QApplication.processEvents()
        # to allow the GUI to update itself )
        QTimer.singleShot(10000, self.stopBar)

    def stopBar(self):
        self.busyBar.Kill()                        # Close looping progress bar

app = QApplication(sys.argv)
win = LayoutCreator()
win.show();
sys.exit(app.exec_())

