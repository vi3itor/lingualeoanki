import locale
import sys

import platform
import socket
import urllib.error

from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *

from . import connect
from . import utils
from . import styles

# TODO: Make Russian localization
#  (since beginners are more comfortable with native language)

class PluginWindow(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Import from LinguaLeo')

        # Window Icon
        if platform.system() == 'Windows':
            path = os.path.join(os.path.dirname(__file__), 'favicon.ico')
            # Check Python version for Anki 2.0 support (in the future)
            if sys.version_info[0] < 3:
                loc = locale.getdefaultlocale()[1]
                path = path.decode(loc)
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
        #  with typing correct answer or without (or use config for that purpose)

        radio_buttons = QHBoxLayout()
        self.rbutton_all = QRadioButton("All")
        self.rbutton_studied = QRadioButton("Studied")
        self.rbutton_unstudied = QRadioButton("Unstudied")
        self.rbutton_all.setChecked(True)
        radio_buttons.addWidget(self.rbutton_all)
        radio_buttons.addWidget(self.rbutton_studied)
        radio_buttons.addWidget(self.rbutton_unstudied)

        # Main layout - vertical box
        vbox = QVBoxLayout()

        # Form layouts
        login_form = QFormLayout()
        login_form.addRow(loginLabel, self.loginField)
        login_form.addRow(passLabel, self.passField)
        login_form.addRow(self.checkBoxRememberPassLabel, self.checkBoxRememberPass)

        fbox = QFormLayout()
        fbox.addRow(radio_buttons)
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
        self.rbutton_all.setEnabled(False)
        self.rbutton_studied.setEnabled(False)
        self.rbutton_unstudied.setEnabled(False)

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

        # TODO: Support Anki 2.0 by manually reading config from json
        # Load config file
        self.config = mw.addonManager.getConfig(__name__)
        if self.config['rememberPassword'] == 1:
            self.checkBoxRememberPass.setChecked(True)
            self.loginField.setText(self.config['email'])
            self.passField.setText(self.config['password'])

        self.show()

    def loginButtonClicked(self):
        # Save login and password
        self.login = self.loginField.text()
        self.password = self.passField.text()

        # TODO: Support Anki 2.0 by manually writing json to config
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
        # TODO if login or pass doesn't match or there is no internet connection
        #  don't enable other buttons
        self.authorization.Error.connect(self.showErrorMessage)
        self.authorization.get_connection()

        # Disable login button and fields
        self.loginButton.setEnabled(False)
        self.loginField.setEnabled(False)
        self.passField.setEnabled(False)
        self.checkBoxRememberPass.setEnabled(False)

        # Enable all other buttons
        self.logoutButton.setEnabled(True)
        self.set_download_form_enabled(True)

    def logoutButtonClicked(self):
        # Disable logout and other buttons
        self.logoutButton.setEnabled(False)
        self.set_download_form_enabled(False)

        self.authorization = None
        # TODO: Delete cookies here when they are implemented

        # Enable Login button and fields
        self.loginButton.setEnabled(True)
        self.loginField.setEnabled(True)
        self.passField.setEnabled(True)
        self.checkBoxRememberPass.setEnabled(True)

    def importAllButtonClicked(self):
        # Disable buttons
        self.set_download_form_enabled(False)
        self.start_download_thread()

    def wordsetButtonClicked(self):
        self.set_download_form_enabled(False)

        # TODO: Process exceptions of get_wordsets()
        wordset_window = WordsetsWindow(self.authorization)
        wordset_window.Wordsets.connect(self.start_download_thread)
        wordset_window.Error.connect(self.showErrorMessage)
        wordset_window.exec_()

    def start_download_thread(self, wordsets=None):
        # Activate progress bar
        self.progressBar.setValue(0)
        self.progressBar.show()
        self.progressLabel.show()

        # Set Anki Model
        self.set_model()

        # Get user's choice of words: {'Studied', 'Unstudied', 'All'}
        progress = self.get_progress_type()

        # Start downloading
        self.threadclass = Download(self.login, self.password, progress, wordsets)
        self.threadclass.start()
        self.threadclass.Length.connect(self.progressBar.setMaximum)
        self.threadclass.Word.connect(self.addWord)
        self.threadclass.Counter.connect(self.progressBar.setValue)
        self.threadclass.FinalCounter.connect(self.setFinalCount)
        self.threadclass.Error.connect(self.setErrorMessage)
        self.threadclass.finished.connect(self.downloadFinished)

    def set_model(self):
        self.model = utils.prepare_model(mw.col, utils.fields, styles.model_css)

    def get_progress_type(self):
        progress = 'All'
        if self.rbutton_studied.isChecked():
            progress = 'Studied'
        elif self.rbutton_unstudied.isChecked():
            progress = 'Unstudied'
        return progress

    def set_download_form_enabled(self, mode):
        """
        Set buttons either enabled or disabled
        :param mode: True or False
        """
        self.importAllButton.setEnabled(mode)
        self.importByDictionaryButton.setEnabled(mode)
        self.rbutton_all.setEnabled(mode)
        self.rbutton_studied.setEnabled(mode)
        self.rbutton_unstudied.setEnabled(mode)

    def addWord(self, word):
        """
        Note is an SQLite object in Anki so you need
        to fill it out inside the main thread
        """
        utils.add_word(word, self.model)

    def cancelButtonClicked(self):
        if hasattr(self, 'threadclass') and not self.threadclass.isFinished():
            self.threadclass.terminate()
        # Delete attribute before closing to allow running the plugin again
        delattr(mw, 'lingualeoanki')
        mw.reset()
        self.close()

    def setFinalCount(self, counter):
        self.wordsFinalCount = counter

    def setErrorMessage(self, msg):
        self.errorMessage = msg

    def showErrorMessage(self, msg):
        showInfo(msg)
        mw.reset()

    def downloadFinished(self):
        if hasattr(self, 'wordsFinalCount'):
            showInfo("%d words from LinguaLeo have been processed" % self.wordsFinalCount)
        if hasattr(self, 'errorMessage'):
            self.showErrorMessage(self.errorMessage)

        self.set_download_form_enabled(True)

        self.progressLabel.hide()
        self.progressBar.hide()
        mw.reset()


class WordsetsWindow(QDialog):
    Wordsets = pyqtSignal(list)
    Error = pyqtSignal(str)

    def __init__(self, authorization, parent=None):
        QDialog.__init__(self, parent)
        self.authorization = authorization
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Choose dictionaries to import')

        # Buttons and fields
        self.importButton = QPushButton("Import", self)
        self.cancelButton = QPushButton("Cancel", self)
        self.importButton.clicked.connect(self.importButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        key_name = 'Cmd'
        if platform.system() == 'Windows' or platform.system() == 'Linux':
            key_name = 'Ctrl'
        label = QLabel('Hold ' + key_name + ' to select several dictionaries')
        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # TODO: Activate Import button only when some dictionary is selected

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.listWidget)

        self.authorization.Error.connect(self.emit_error_message)
        self.wordsets = self.authorization.get_wordsets()

        if not self.wordsets:
            self.emit_error_message("No user dictionaries found")

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

    def emit_error_message(self, msg):
        self.Error.emit(msg)
        mw.reset()
        self.close()


class Download(QThread):
    Length = pyqtSignal(int)
    Error = pyqtSignal(str)
    Word = pyqtSignal(dict)
    Counter = pyqtSignal(int)
    FinalCounter = pyqtSignal(int)

    def __init__(self, login, password, progress, wordsets, parent=None):
        QThread.__init__(self, parent)
        self.login = login
        self.password = password
        self.progress = progress
        if wordsets:
            self.wordsets = wordsets

    def run(self):
        # Check if wordsets attribute exists
        wordsets = getattr(self, 'wordsets', None)
        words = self.get_words_to_add(wordsets)
        if words:
            self.Length.emit(len(words))
            self.add_separately(words)
        else:
            msg = "No words to download"
            if not self.progress == 'All':
                msg = "No " + self.progress + " words to download"
            self.Error.emit(msg)

    def get_connection(self):
        self.leo = connect.Lingualeo(self.login, self.password)
        try:
            # TODO: for cookies: if not self.leo.is_authorized():
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
            self.msg = ''
            return None

    def get_wordsets(self):
        self.get_connection()
        return self.leo.get_wordsets()

    def get_words_to_add(self, wordsets=None):
        self.get_connection()
        try:
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
            self.msg = ''
            return None
        if self.progress == 'Unstudied':
            words = [word for word in words if word.get('progress_percent') < 100]
        elif self.progress == 'Studied':
            words = [word for word in words if word.get('progress_percent') == 100]

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
