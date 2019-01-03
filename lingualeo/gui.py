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

        # Login section widgets
        loginLabel = QLabel('Your LinguaLeo Login:')
        self.loginField = QLineEdit()
        passLabel = QLabel('Your LinguaLeo Password:')
        self.passField = QLineEdit()
        self.passField.setEchoMode(QLineEdit.Password)
        self.loginButton = QPushButton("Log In")
        self.logoutButton = QPushButton("Log Out")
        self.loginButton.clicked.connect(self.loginButtonClicked)
        self.logoutButton.clicked.connect(self.logoutButtonClicked)
        self.checkBoxRememberPass = QCheckBox()
        self.checkBoxRememberPassLabel = QLabel('Remember password')

        # Import section widgets
        # TODO: Add tooltip with explanation: it will not replace already existing words
        self.importAllButton = QPushButton("Import all words")
        self.importByDictionaryButton = QPushButton("Import from dictionaries")
        self.cancelButton = QPushButton("Cancel")
        self.importAllButton.clicked.connect(self.importAllButtonClicked)
        self.importByDictionaryButton.clicked.connect(self.wordsetButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        self.progressLabel = QLabel('Downloading Progress:')
        self.progressBar = QProgressBar()

        # TODO: Implement GUI element to ask what style cards to create:
        #  with typing correct answer or without

        # TODO Replace checkbox with radiobutton (Studied or Unstudied or All)
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
        # TODO: make buttons smaller
        login_buttons.addWidget(self.loginButton)
        login_buttons.addWidget(self.logoutButton)

        # Horizontal layout for import buttons
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.importAllButton)
        hbox.addWidget(self.importByDictionaryButton)
        hbox.addWidget(self.cancelButton)
        hbox.addStretch()

        # Disable buttons
        self.logoutButton.setEnabled(False)
        self.importAllButton.setEnabled(False)
        self.importByDictionaryButton.setEnabled(False)
        self.checkBoxUnstudied.setEnabled(False)

        # Add layouts to main layout
        vbox.addLayout(login_form)
        vbox.addLayout(login_buttons)
        vbox.addStretch()
        vbox.addLayout(fbox)
        vbox.addStretch()
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

    def loginButtonClicked(self):
        # Save login and password
        self.login = self.loginField.text()
        self.password = self.passField.text()

        # Save email and password to config if they differ
        if (self.config['email'] != self.login or
            self.config['password'] != self.password):
            # Write config only if it is different
            if self.checkBoxRememberPass.checkState():
                self.config['email'] = self.login
                self.config['password'] = self.password
                self.config['rememberPassword'] = 1
            else:
                self.config['email'] = ''
                self.config['password'] = ''
                self.config['rememberPassword'] = 0

            mw.addonManager.writeConfig(__name__, self.config)

        self.authorization = Download(self.login, self.password, None, None)
        # TODO Process incorrect login or password and don't close window
        #  if login or pass doesn't match or there is no internet connection
        self.authorization.Error.connect(self.showErrorMessage)
        self.authorization.get_connection()

        # Disable login button and fields
        self.loginButton.setEnabled(False)
        self.loginField.setEnabled(False)
        self.passField.setEnabled(False)
        self.checkBoxRememberPass.setEnabled(False)

        # Enable all other buttons
        self.logoutButton.setEnabled(True)
        self.importAllButton.setEnabled(True)
        self.importByDictionaryButton.setEnabled(True)
        self.checkBoxUnstudied.setEnabled(True)

    def logoutButtonClicked(self):
        # Disable logout and other buttons
        self.logoutButton.setEnabled(False)
        self.importAllButton.setEnabled(False)
        self.importByDictionaryButton.setEnabled(False)
        self.checkBoxUnstudied.setEnabled(False)

        self.authorization = None
        # Enable Login button and fields
        self.loginButton.setEnabled(True)
        self.loginField.setEnabled(True)
        self.passField.setEnabled(True)
        self.checkBoxRememberPass.setEnabled(True)

        # TODO: Delete cookies here when they are implemented

    def importAllButtonClicked(self):

        unstudied = self.checkBoxUnstudied.checkState()
        self.importAllButton.setEnabled(False)
        self.checkBoxUnstudied.setEnabled(False)

        self.start_download_thread(self.login, self.password, unstudied)

    def wordsetButtonClicked(self):
        unstudied = self.checkBoxUnstudied.checkState()

        self.importAllButton.setEnabled(False)
        self.importByDictionaryButton.setEnabled(False)

        # TODO: Process exceptions of get_wordsets()
        wordset_window = WordsetsWindow(self.login, self.password, unstudied, self.authorization)
        wordset_window.Wordsets.connect(self.import_wordset_words)
        wordset_window.exec_()
        self.importAllButton.setEnabled(True)
        self.importByDictionaryButton.setEnabled(True)

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

    def cancelButtonClicked(self):
        if hasattr(self, 'threadclass') and not self.threadclass.isFinished():
            self.threadclass.terminate()
        mw.reset()
        self.close()

    def setFinalCount(self, counter):
        self.wordsFinalCount = counter

    def setErrorMessage(self, msg):
        self.errorMessage = msg

    def showErrorMessage(self, msg):
        showInfo(msg)
        mw.reset()
        self.close()

    def downloadFinished(self):
        if hasattr(self, 'wordsFinalCount'):
            showInfo("%d words from LinguaLeo have been processed" % self.wordsFinalCount)
        if hasattr(self, 'errorMessage'):
            showInfo(self.errorMessage)
        mw.reset()
        self.close()


class WordsetsWindow(QDialog):
    Wordsets = pyqtSignal(list)

    def __init__(self, login, password, unstudied, download, parent=None):
        QDialog.__init__(self, parent)
        self.login = login
        self.password = password
        self.unstudied = unstudied
        self.download = download
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Choose dictionaries to import')

        # Buttons and fields
        self.importButton = QPushButton("Import", self)
        self.cancelButton = QPushButton("Cancel", self)
        self.importButton.clicked.connect(self.importButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        label = QLabel("Hold Ctrl (Cmd) to pick several dictionaries")
        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.listWidget)

        self.download.Error.connect(self.show_error_message)
        self.wordsets = self.download.get_wordsets()

        if not self.wordsets:
            self.show_error_message("No dictionaries found")

        for wordset in self.wordsets:
            item_name = wordset['name'] + ' (' + str(wordset['countWords']) + ' words)'
            item = QListWidgetItem(item_name)
            item.wordset_id = wordset['id']
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
        selected_ids = []
        for i in range(len(items)):
            selected_ids.append(str(items[i].wordset_id))

        selected_wordsets = []

        for wordset in self.wordsets:
            if str(wordset['id']) in selected_ids:
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

    def run(self):
        # Check if wordsets attribute exists
        wordsets = getattr(self, 'wordsets', None)
        words = self.get_words_to_add(wordsets)
        if words:
            self.Length.emit(len(words))
            self.add_separately(words)

    def get_connection(self):
        self.leo = connect.Lingualeo(self.login, self.password)
        try:
            if not self.leo.is_authorized():
                status = self.leo.auth()
                if status['error_msg']:
                    self.msg = status['error_msg']
        except urllib.error.URLError:
            self.msg = "Can't authorize. Check your internet connection."
        except ValueError:
            # TODO improve exception handling
            self.msg = "Value error"
        except:
            self.msg = "There's been an unexpected error. Sorry about that!"
        if hasattr(self, 'msg'):
            self.Error.emit(self.msg)
            return None

    def get_wordsets(self):
        self.get_connection()
        return self.leo.get_wordsets()

    def get_words_to_add(self, wordsets=None):
        try:
            self.get_connection()
            if wordsets:
                words = self.leo.get_words_by_wordsets(wordsets)
            # Import all words
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

        # TODO: in utils prepare a list of not duplicates first and then send to download

        # TODO: check if reversed is needed
        for word in reversed(words):
            self.Word.emit(word)
            try:
                utils.send_to_download(word, self)
            except (urllib.error.URLError, socket.error):
                problem_words.append(word.get('word_value'))
            counter += 1
            # TODO Show numbers in progress bar
            self.Counter.emit(counter)
        self.FinalCounter.emit(counter)

        # TODO: save problem words in json format to user_files folder
        #  and ask user to retry downloading problem words

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
