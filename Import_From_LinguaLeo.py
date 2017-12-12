# -*- coding: utf-8 -*-
import locale
import os
from anki import notes
from aqt import mw  
from aqt.qt import QAction
from aqt.utils import showInfo
from import_from_lingualeo import connect
from import_from_lingualeo.utils import *
from PyQt4.QtGui import QDialog, QIcon, QPushButton, QHBoxLayout, QVBoxLayout, QLineEdit, QFormLayout, QLabel, QProgressBar, QCheckBox 
from PyQt4.QtCore import QThread, SIGNAL
  
class PluginWindow(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('Import From LinguaLeo')  
        
        # Window Icon
        path = os.path.join(os.path.dirname(__file__), 'import_from_lingualeo', 'favicon.ico')
        loc = locale.getdefaultlocale()[1] 
        path = unicode(path, loc)
        self.setWindowIcon(QIcon(path))               
        
        # Buttons and fields
        self.importButton = QPushButton("Import", self)  
        self.cancelButton = QPushButton("Cancel", self)
        self.importButton.clicked.connect(self.importButtonClicked) 
        self.cancelButton.clicked.connect(self.cancelButtonClicked)        
        loginLabel = QLabel('Your LinguaLeo Login:')
        self.loginField = QLineEdit()        
        passLabel = QLabel('Your LinguaLeo Password:')
        self.passField = QLineEdit()
        self.passField.setEchoMode(QLineEdit.Password)
        self.progressLabel = QLabel('Downloading Progress:')
        self.progressBar = QProgressBar()        
        self.checkBox = QCheckBox()
        self.checkBoxLabel = QLabel('Unstudied only?')
        
        # Main layout - vertical box
        vbox = QVBoxLayout()
 
        # Form layout        
        fbox = QFormLayout()
        fbox.setMargin(10)
        fbox.addRow(loginLabel, self.loginField)
        fbox.addRow(passLabel, self.passField)
        fbox.addRow(self.progressLabel, self.progressBar)
        fbox.addRow(self.checkBoxLabel, self.checkBox)
        self.progressLabel.hide()
        self.progressBar.hide()
        
        # Horizontal layout for buttons
        hbox = QHBoxLayout()
        hbox.setMargin(10)
        hbox.addStretch()
        hbox.addWidget(self.importButton)        
        hbox.addWidget(self.cancelButton)
        hbox.addStretch()
        
        # Add form layout, then stretch and then buttons in main layout
        vbox.addLayout(fbox)
        vbox.addStretch(2)
        vbox.addLayout(hbox)
      
        # Set main layout
        self.setLayout(vbox)
        # Set focus for typing from the keyboard
        # You have to do it after creating all widgets
        self.loginField.setFocus()
      
        self.show()
        
    def importButtonClicked(self):
        self.importButton.setEnabled(False)
        self.progressLabel.show()
        self.progressBar.show()
        login = self.loginField.text()
        password = self.passField.text()        
        unstudied = self.checkBox.checkState()
        
        self.threadclass = Download(login, password, unstudied)
        self.threadclass.start()
        self.connect(self.threadclass, SIGNAL('Length'), self.progressBar.setMaximum)
        self.connect(self.threadclass, SIGNAL('Word'), self.addWord)
        self.connect(self.threadclass, SIGNAL('Counter'), self.progressBar.setValue)
        self.connect(self.threadclass, SIGNAL('FinalCounter'), self.setFinalCount)
        self.threadclass.finished.connect(self.downloadFinished)
    
    def cancelButtonClicked(self):
        if hasattr(self, 'threadclass') and not self.threadclass.isFinished():
            self.threadclass.quit()
        mw.reset()    
        self.close()
        
    def addWord(self, input):
        word, model, destination_folder = input
        collection = mw.col
        note = notes.Note(collection, model)
        # Note is an SQLite object in Anki so you need to fill it out
        # inside the main thread
        note = fill_note(word, note, destination_folder)
        collection.addNote(note)
    
    def setFinalCount(self, counter):
        self.wordsFinalCount = counter
    
    def downloadFinished(self): 
        if hasattr(self, 'wordsFinalCount'):
            showInfo("You have %d new words" % self.wordsFinalCount)
        mw.reset()
        self.close() 
        
        
class Download(QThread):
    def __init__(self, login, password, unstudied, parent=None):
        QThread.__init__(self, parent)
        self.login = login
        self.password = password
        self.unstudied = unstudied

    def run(self):
        collection = mw.col        
        lingualeo = connect.Lingualeo(self.login, self.password)
        lingualeo.get_all_words()
        words = lingualeo.userdict
        if self.unstudied:
            words = [word for word in words if word.get('progress_percent') < 100]
        self.emit(SIGNAL('Length'), len(words))
        model = prepare_model(collection, fields, model_css)
        destination_folder = collection.media.dir()        
        counter = 0
        for word in words:
            self.emit(SIGNAL('Word'), (word, model, destination_folder))            
            # Divides downloading and filling note to different threads
            # because you cannot create SQLite objects outside the main thread in Anki
            # Also you cannot download files in the main thread because it will freeze GUI
            send_to_download(word, destination_folder)           
            counter += 1
            self.emit(SIGNAL('Counter'), counter)      
        self.emit(SIGNAL('FinalCounter'), counter)

        
def activate():
    window = PluginWindow()
    window.exec_()        

# create a new menu item
action = QAction("Import From LinguaLeo", mw)
# set it to call a function when it's clicked
action.triggered.connect(activate)
# and add it to the tools menu
mw.form.menuTools.addAction(action)
