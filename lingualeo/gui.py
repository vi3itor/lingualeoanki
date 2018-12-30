# -*- coding: utf-8 -*-
import locale

import platform
import socket
import urllib.error

from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *

from . import connect
from . import utils
from . import styles


class PluginWindow(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Import from LinguaLeo')

        # Window Icon
        if platform.system() == 'Windows':
            path = os.path.join(os.path.dirname(__file__), 'favicon.ico')
            loc = locale.getdefaultlocale()[1]
            path = str(path, loc)
            self.setWindowIcon(QIcon(path))

        # Login section
        loginLabel = QLabel('Your LinguaLeo Login:')
        self.loginField = QLineEdit()
        passLabel = QLabel('Your LinguaLeo Password:')
        self.passField = QLineEdit()
        self.passField.setEchoMode(QLineEdit.Password)
        self.loginButton = QPushButton("Log In")
        self.logoutButton = QPushButton("Log Out")

        # Buttons and fields
        # TODO: Add tooltip with explanation: it will not replace already existing words
        self.importAllButton = QPushButton("Import all words", self)
        # TODO Rename buttons appropriately
        self.wordsetButton = QPushButton("Import from dictionaries", self)
        self.cancelButton = QPushButton("Close", self)
        self.importAllButton.clicked.connect(self.importAllButtonClicked)
        self.wordsetButton.clicked.connect(self.wordsetButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        self.progressLabel = QLabel('Downloading Progress:')
        self.progressBar = QProgressBar()
        self.checkBoxRememberPass = QCheckBox()
        self.checkBoxRememberPassLabel = QLabel('Remember password')

        # TODO Replace checkbox with radiobutton (Unstudied or Studied or All)
        self.checkBoxUnstudied = QCheckBox()
        self.checkBoxUnstudiedLabel = QLabel('Unstudied only')

        # Main layout - vertical box
        vbox = QVBoxLayout()

        # Form layouts
        login_form = QFormLayout()
        login_form.addRow(loginLabel, self.loginField)
        login_form.addRow(passLabel, self.passField)
        login_form.addRow(self.checkBoxRememberPassLabel, self.checkBoxRememberPass)

        fbox = QFormLayout()
        fbox.addRow(self.checkBoxUnstudiedLabel, self.checkBoxUnstudied)
        fbox.addRow(self.progressLabel, self.progressBar)
        self.progressLabel.hide()
        self.progressBar.hide()

        # Horizontal layout for login buttons
        login_buttons = QHBoxLayout()
        login_buttons.setContentsMargins(10, 10, 10, 10)
        login_buttons.addWidget(self.loginButton)
        login_buttons.addWidget(self.logoutButton)

        # Horizontal layout for import buttons
        hbox = QHBoxLayout()
        hbox.setContentsMargins(10, 10, 10, 10)
        hbox.addStretch()
        hbox.addWidget(self.importAllButton)
        hbox.addWidget(self.wordsetButton)
        hbox.addWidget(self.cancelButton)
        hbox.addStretch()

        # Add layouts to main layout
        vbox.addLayout(login_form)
        vbox.addStretch()
        vbox.addLayout(login_buttons)
        vbox.addStretch(2)
        vbox.addLayout(fbox)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        # Set main layout
        self.setLayout(vbox)
        # Set focus for typing from the keyboard
        # You have to do it after creating all widgets
        self.loginField.setFocus()

        # Load config file
        self.config = mw.addonManager.getConfig('lingualeoanki')
        if self.config['rememberPassword'] == 1:
            self.checkBoxRememberPass.setChecked(True)
            self.loginField.setText(self.config['email'])
            self.passField.setText(self.config['password'])

        self.show()

    def importAllButtonClicked(self):
        login = self.loginField.text()
        password = self.passField.text()

        # Save email and password to config
        if self.checkBoxRememberPass.checkState():
            self.config['email'] = login
            self.config['password'] = password
            self.config['rememberPassword'] = 1
            mw.addonManager.writeConfig(__name__, self.config)

        unstudied = self.checkBoxUnstudied.checkState()
        self.importAllButton.setEnabled(False)
        self.checkBoxUnstudied.setEnabled(False)

        self.start_download_thread(login, password, unstudied)

    def wordsetButtonClicked(self):
        login = self.loginField.text()
        password = self.passField.text()
        unstudied = self.checkBoxUnstudied.checkState()

        self.importAllButton.setEnabled(False)
        self.wordsetButton.setEnabled(False)

        wordset_window = WordsetsWindow(login, password, unstudied)
        wordset_window.Wordsets.connect(self.import_wordset_words)
        wordset_window.exec_()

    def import_wordset_words(self, wordsets):
        login = self.loginField.text()
        password = self.passField.text()
        unstudied = self.checkBoxUnstudied.checkState()
        self.start_download_thread(login, password, unstudied, wordsets)

    def start_download_thread(self, login, password, unstudied, wordsets=None):
        # Activate progress bar
        self.progressLabel.show()
        self.progressBar.show()
        self.progressBar.setValue(0)

        # Set Anki Model
        self.set_model()

        # Start downloading
        self.threadclass = Download(login, password, unstudied, wordsets)
        self.threadclass.start()
        self.threadclass.Length.connect(self.progressBar.setMaximum)
        self.threadclass.Word.connect(self.addWord)
        self.threadclass.Counter.connect(self.progressBar.setValue)
        self.threadclass.FinalCounter.connect(self.setFinalCount)
        self.threadclass.Error.connect(self.setErrorMessage)
        self.threadclass.finished.connect(self.downloadFinished)

    def set_model(self):
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


class WordsetsWindow(QDialog):
    Wordsets = pyqtSignal(list)

    def __init__(self, login, password, unstudied, parent=None):
        QDialog.__init__(self, parent)
        self.initUI(login, password, unstudied)

    def initUI(self, login, password, unstudied):

        self.setWindowTitle('Choose dictionaries to import')

        # Buttons and fields
        self.importButton = QPushButton("Import", self)
        self.cancelButton = QPushButton("Cancel", self)
        self.importButton.clicked.connect(self.importButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        label = QLabel("Hold Ctrl (Cmd) to pick several dictionaries")
        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # TODO: check if setGeometry is needed
        # self.listWidget.setGeometry(QRect(10, 10, 211, 291))

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.listWidget)

        download = Download(login, password, unstudied, wordsets=None)
        download.Error.connect(self.show_error_message)
        self.wordsets = download.get_wordsets()

        if not self.wordsets:
            self.show_error_message("No dictionaries found")

        for wordset in self.wordsets:
            item_name = wordset['name'] + ' (' + str(wordset['countWords']) + ' words)'
            item = QListWidgetItem(item_name)
            self.listWidget.addItem(item)

        self.layout.addWidget(label)

        # Horizontal layout for buttons
        hbox = QHBoxLayout()
        hbox.setContentsMargins(10, 10, 10, 10)
        hbox.addStretch()

        hbox.addWidget(self.importButton)
        hbox.addWidget(self.cancelButton)
        self.layout.addLayout(hbox)
        self.setLayout(self.layout)
        self.show()

    def importButtonClicked(self):
        items = self.listWidget.selectedItems()
        selected_names = []
        for i in range(len(items)):
            selected_names.append(str(self.listWidget.selectedItems()[i].text()))

        selected_wordsets = []

        for wordset in self.wordsets:
            if wordset['name'] in selected_names:
                selected_wordsets.append(wordset.copy())

        self.Wordsets.emit(selected_wordsets)
        mw.reset()
        self.close()

    def cancelButtonClicked(self):
        mw.reset()
        self.close()

    def show_error_message(self, msg):
        showInfo(msg)
        mw.reset()
        self.close()


class Download(QThread):
    Length = pyqtSignal(int)
    Error = pyqtSignal(str)
    Word = pyqtSignal(dict)
    Counter = pyqtSignal(int)
    FinalCounter = pyqtSignal(int)

    def __init__(self, login, password, unstudied, wordsets, parent=None):
        QThread.__init__(self, parent)
        self.login = login
        self.password = password
        self.unstudied = unstudied
        if wordsets:
            self.wordsets = wordsets

    # TODO: Consider the order of buttons clicked and reimplement run method
    def run(self):
        self.get_connection(self.login, self.password)
        # Check if wordsets attribute exists
        wordsets = getattr(self, 'wordsets', None)
        words = self.get_words_to_add(wordsets)
        if words:
            self.Length.emit(len(words))
            self.add_separately(words)

    def get_connection(self, login, password):
        self.leo = connect.Lingualeo(login, password)
        try:
            status = self.leo.auth()
        except urllib.error.URLError:
            self.msg = "Can't authorize. Check your internet connection."
        except ValueError:
            try:
                self.msg = status['error_msg']
            except:
                self.msg = "There's been an unexpected error. Sorry about that!"
        if hasattr(self, 'msg'):
            self.Error.emit(self.msg)
            return None

    def get_wordsets(self):
        self.get_connection(self.login, self.password)
        return self.leo.get_wordsets()

    def get_words_to_add(self, wordsets=None):
        try:
            if wordsets:
                words = self.leo.get_words_by_wordsets(wordsets)
            else:
                words = self.leo.get_all_words()
        except urllib.error.URLError:
            self.msg = "Can't download words. Check your internet connection."
        except ValueError:
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

        # TODO: utils have to prepare a list of not duplicates first and then send to download

        for word in reversed(words):
            self.Word.emit(word)
            try:
                utils.send_to_download(word, self)
            except (urllib.error.URLError, socket.error) as e:
                problem_words.append(word.get('word_value'))
            counter += 1
            self.Counter.emit(counter)
        self.FinalCounter.emit(counter)

        # TODO: save problem words in json format to user_files folder
        # TODO: ask user to retry downloading problem words

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
