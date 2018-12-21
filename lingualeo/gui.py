# -*- coding: utf-8 -*-
import locale
#from PyQt5.QtWidgets import *
import os
import platform
import socket
import urllib.request, urllib.error, urllib.parse

from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
#from PyQt5.QtCore import QThread, pyqtSignal

from . import connect
from . import utils
from . import styles


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
            path = str(path, loc)
            self.setWindowIcon(QIcon(path))

        # Load config file
        self.config = mw.addonManager.getConfig('lingualeoanki')

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
        self.checkBoxRememberPass = QCheckBox()
        self.checkBoxRememberPassLabel = QLabel('Remember password')
        self.checkBoxUnstudied = QCheckBox()
        self.checkBoxUnstudiedLabel = QLabel('Unstudied only')
        # self.checkBoxMissed = QCheckBox()
        # self.checkBoxLabelMissed = QLabel('Missed words?')

        # Main layout - vertical box
        vbox = QVBoxLayout()

        # Form layout
        fbox = QFormLayout()
        fbox.addRow(loginLabel, self.loginField)
        fbox.addRow(passLabel, self.passField)
        fbox.addRow(self.checkBoxRememberPassLabel, self.checkBoxRememberPass)
        fbox.addRow(self.progressLabel, self.progressBar)
        fbox.addRow(self.checkBoxUnstudiedLabel, self.checkBoxUnstudied)
        # fbox.addRow(self.checkBoxLabelMissed, self.checkBoxMissed)
        self.progressLabel.hide()
        self.progressBar.hide()

        # Horizontal layout for buttons
        hbox = QHBoxLayout()
        hbox.setContentsMargins(10, 10, 10, 10)
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
        if self.config['rememberPassword'] == 1:
            self.checkBoxRememberPass.setChecked(True)
            self.loginField.setText(self.config['email'])
            self.passField.setText(self.config['password'])

        self.show()

    def importButtonClicked(self):
        login = self.loginField.text()
        password = self.passField.text()
        if self.checkBoxRememberPass.checkState():
            self.config['email'] = login
            self.config['password'] = password
            self.config['rememberPassword'] = 1
            mw.addonManager.writeConfig(__name__, self.config)

        unstudied = self.checkBoxUnstudied.checkState()
        # missed = self.checkBoxMissed.checkState()
        self.importButton.setEnabled(False)
        self.checkBoxUnstudied.setEnabled(False)
        # self.checkBoxMissed.setEnabled(False)
        self.progressLabel.show()
        self.progressBar.show()
        self.progressBar.setValue(0)

        # Run before lastWord() to create a model if it doesn't exist
        self.setModel()
        # Find last word to work "missed function"
        # last_word = self.lastWord()

        self.threadclass = Download(login, password, unstudied)  # , missed, last_word)
        self.threadclass.start()
        self.threadclass.Length.connect(self.progressBar.setMaximum)
        self.threadclass.Word.connect(self.addWord)
        self.threadclass.Counter.connect(self.progressBar.setValue)
        self.threadclass.FinalCounter.connect(self.setFinalCount)
        self.threadclass.Error.connect(self.setErrorMessage)
        self.threadclass.finished.connect(self.downloadFinished)

    def setModel(self):
        self.model = utils.prepare_model(mw.col, utils.fields, styles.model_css)

    def addWord(self, word):
        """
        Note is an SQLite object in Anki so you need
        to fill it out inside the main thread
        """
        utils.add_word(word, self.model)

    # def lastWord(self):
    #     last_word = utils.get_the_last_word()
    #     return last_word;

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
            showInfo("%d words from LinguaLeo have been processed" % self.wordsFinalCount)
        if hasattr(self, 'errorMessage'):
            showInfo(self.errorMessage)
        mw.reset()
        self.close()


class Download(QThread):
    Length = pyqtSignal(int)
    Error = pyqtSignal(str)
    Word = pyqtSignal(dict)
    Counter = pyqtSignal(int)
    FinalCounter = pyqtSignal(int)

    def __init__(self, login, password, unstudied, parent=None):  # , missed, last_word removed
        QThread.__init__(self, parent)
        self.login = login
        self.password = password
        self.unstudied = unstudied
        # self.missed = missed
        # self.last_word = last_word

    def run(self):
        words = self.get_words_to_add()
        if words:
            self.Length.emit(len(words))  # removed argument len(words)
            self.add_separately(words)

    def get_words_to_add(self):
        leo = connect.Lingualeo(self.login, self.password)
        try:
            status = leo.auth()
            words = leo.get_all_words()  # self.missed, self.last_word)
        except urllib.error.URLError:
            self.msg = "Can't download words. Check your internet connection."
        except ValueError:
            try:
                self.msg = status['error_msg']
            except:
                self.msg = "There's been an unexpected error. Sorry about that!"
        if hasattr(self, 'msg'):
            self.Error.emit(self.msg)
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
        for word in reversed(words):
            self.Word.emit(word)
            try:
                utils.send_to_download(word, self)
            except (urllib.error.URLError, socket.error) as e:
                problem_words.append(word.get('word_value'))
            counter += 1
            self.Counter.emit(counter)
        self.FinalCounter.emit(counter)
        if problem_words:
            self.problem_words_msg(problem_words)

    def problem_words_msg(self, problem_words):
        error_msg = ("We weren't able to download media for these "
                     "words because of broken links in LinguaLeo "
                     "or problems with an internet connection: ")
        for problem_word in problem_words[:-1]:
            error_msg += problem_word + ', '
        error_msg += problem_words[-1] + '.'
        self.Error.emit(error_msg)
