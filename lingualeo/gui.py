# -*- coding: utf-8 -*-
import locale
import os
import platform
import socket
import urllib2

from anki import notes
from aqt import mw
from aqt.utils import showInfo
from PyQt4.QtGui import (QDialog, QIcon, QPushButton, QHBoxLayout,
                         QVBoxLayout, QLineEdit, QFormLayout,
                         QLabel, QProgressBar, QCheckBox)
from PyQt4.QtCore import QThread, SIGNAL

from lingualeo import connect
from lingualeo import utils
from lingualeo import styles


class PluginWindow(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Import From LinguaLeo')

        # Window Icon
        if platform.system() == 'Windows':
            path = os.path.join(os.path.dirname(__file__), 'favicon.ico')
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
        login = self.loginField.text()
        password = self.passField.text()
        unstudied = self.checkBox.checkState()
        self.importButton.setEnabled(False)
        self.checkBox.setEnabled(False)
        self.progressLabel.show()
        self.progressBar.show()
        self.progressBar.setValue(0)

        self.threadclass = Download(login, password, unstudied)
        self.threadclass.start()
        self.connect(self.threadclass, SIGNAL('Length'), self.progressBar.setMaximum)
        self.setModel()
        self.connect(self.threadclass, SIGNAL('Word'), self.addWord)
        self.connect(self.threadclass, SIGNAL('Counter'), self.progressBar.setValue)
        self.connect(self.threadclass, SIGNAL('FinalCounter'), self.setFinalCount)
        self.connect(self.threadclass, SIGNAL('Error'), self.setErrorMessage)
        self.threadclass.finished.connect(self.downloadFinished)

    def setModel(self):
        self.model = utils.prepare_model(mw.col, utils.fields, styles.model_css)

    def addWord(self, word):
        """
        Note is an SQLite object in Anki so you need
        to fill it out inside the main thread
        """
        utils.add_word(word, self.model)

    def cancelButtonClicked(self):
        if hasattr(self, 'threadclass') and not self.threadclass.isFinished():
            self.threadclass.terminate()
        mw.reset()
        self.close()

    def setFinalCount(self, counter):
        self.wordsFinalCount = counter

    def setErrorMessage(self, msg):
        self.errorMessage = msg

    def downloadFinished(self):
        if hasattr(self, 'wordsFinalCount'):
            showInfo("You have %d new words" % self.wordsFinalCount)
        if hasattr(self, 'errorMessage'):
            showInfo(self.errorMessage)
        mw.reset()
        self.close()


class Download(QThread):
    def __init__(self, login, password, unstudied, parent=None):
        QThread.__init__(self, parent)
        self.login = login
        self.password = password
        self.unstudied = unstudied

    def run(self):
        words = self.get_words_to_add()
        if words:
            self.emit(SIGNAL('Length'), len(words))
            self.add_separately(words)

    def get_words_to_add(self):
        leo = connect.Lingualeo(self.login, self.password)
        try:
            status = leo.auth()
            words = leo.get_all_words()
        except urllib2.URLError:
            self.msg = "Can't download words. Check your internet connection."
        except ValueError:
            if status.get('error_msg'):
                self.msg = status['error_msg']
            else:
                self.msg = "There's been an unexpected error. Sorry about that!"
        if hasattr(self, 'msg'):
            self.emit(SIGNAL('Error'), self.msg)
            return None
        if self.unstudied:
            words = [word for word in words if word.get('progress_percent') < 100]
        return words

    def add_separately(self, words):
        """
        Divides downloading and filling note to different threads
        because you cannot create SQLite objects outside the main
        thread in Anki. Also you cannot download files in the main
        thread because it will freeze GUI
        """
        counter = 0
        problem_words = []
        for word in words:
            self.emit(SIGNAL('Word'), word)
            try:
                utils.send_to_download(word)
            except (urllib2.URLError, socket.error):
                problem_words.append(word.get('word_value'))
            counter += 1
            self.emit(SIGNAL('Counter'), counter)
        self.emit(SIGNAL('FinalCounter'), counter)
        if problem_words:
            self.problem_words_msg(problem_words)

    def problem_words_msg(self, problem_words):
        error_msg = ("We weren't able to download media for these "
                     "words because of broken links in LinguaLeo "
                     "or problems with an internet connection: ")
        for problem_word in problem_words[:-1]:
            error_msg += problem_word + ', '
        error_msg += problem_words[-1] + '.'
        self.emit(SIGNAL('Error'), error_msg)
