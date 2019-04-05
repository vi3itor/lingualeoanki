import locale
import sys

import platform as pm

from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *

from . import connect
from . import utils
from . import styles
from ._name import ADDON_NAME


# TODO: Make Russian localization
#  (since beginners are more comfortable with native language)

class PluginWindow(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.config = utils.get_config()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Import from LinguaLeo')

        # Window Icon
        if pm.system() == 'Windows':
            path = os.path.join(os.path.dirname(__file__), 'favicon.ico')
            # Check Python version for Anki 2.0 support (in the future)
            if sys.version_info[0] < 3:
                loc = locale.getdefaultlocale()[1]
                path = path.decode(loc)
            self.setWindowIcon(QIcon(path))

        # Login section widgets
        loginLabel = QLabel('Your LinguaLeo login:')
        self.loginField = QLineEdit()
        passLabel = QLabel('Your LinguaLeo password:')
        self.passField = QLineEdit()
        self.passField.setEchoMode(QLineEdit.Password)
        self.loginButton = QPushButton("Log In")
        self.logoutButton = QPushButton("Log Out")
        self.loginButton.clicked.connect(self.loginButtonClicked)
        self.logoutButton.clicked.connect(self.logoutButtonClicked)
        self.checkBoxStayLoggedIn = QCheckBox('Stay logged in')
        self.checkBoxStayLoggedIn.setChecked(True)
        self.checkBoxSavePass = QCheckBox('Save password')

        # Import section widgets
        self.importAllButton = QPushButton("Import all words")
        self.importByDictionaryButton = QPushButton("Import from dictionaries")
        self.exitButton = QPushButton("Exit")
        self.importAllButton.clicked.connect(self.importAllButtonClicked)
        self.importByDictionaryButton.clicked.connect(self.wordsetButtonClicked)
        self.exitButton.clicked.connect(self.close)
        self.rbutton_any = QRadioButton("Any")
        self.rbutton_any.setChecked(True)
        self.rbutton_studied = QRadioButton("Studied")
        self.rbutton_unstudied = QRadioButton("Unstudied")
        self.checkBoxUpdateNotes = QCheckBox('Update existing notes')
        self.progressLabel = QLabel('Downloading Progress:')
        self.progressBar = QProgressBar()

        # TODO: Implement GUI element to ask what style cards to create:
        #  with typing correct answer or without (or use config for that purpose)

        # Login form layout
        login_form = QFormLayout()
        login_form.addRow(loginLabel, self.loginField)
        login_form.addRow(passLabel, self.passField)
        # Vertical layout for checkboxes
        login_checkboxes = QVBoxLayout()
        login_checkboxes.setAlignment(Qt.AlignCenter)
        login_checkboxes.addWidget(self.checkBoxStayLoggedIn)
        login_checkboxes.addWidget(self.checkBoxSavePass)
        # Horizontal layout for login buttons
        login_buttons = QHBoxLayout()
        # Add stretch to make buttons smaller
        login_buttons.addStretch()
        login_buttons.addWidget(self.loginButton)
        login_buttons.addWidget(self.logoutButton)
        login_buttons.addStretch()
        # Horizontal layout for radio buttons and update checkbox
        options_layout = QHBoxLayout()
        options_layout.addStretch()
        options_layout.addWidget(self.rbutton_any)
        options_layout.addWidget(self.rbutton_studied)
        options_layout.addWidget(self.rbutton_unstudied)
        options_layout.addSpacing(15)
        options_layout.addWidget(self.checkBoxUpdateNotes)
        options_layout.addStretch()
        # Form layout for option buttons and progress bar
        progress_layout = QFormLayout()
        progress_layout.addRow(options_layout)
        progress_layout.addRow(self.progressLabel, self.progressBar)
        # Horizontal layout for import and exit buttons
        imp_btn_layout = QHBoxLayout()
        imp_btn_layout.addStretch()
        imp_btn_layout.addWidget(self.importAllButton)
        imp_btn_layout.addWidget(self.importByDictionaryButton)
        imp_btn_layout.addWidget(self.exitButton)
        imp_btn_layout.addStretch()
        # Main layout
        main_layout = QVBoxLayout()
        # Add layouts to main layout
        main_layout.addLayout(login_form)
        main_layout.addLayout(login_checkboxes)
        main_layout.addLayout(login_buttons)
        main_layout.addLayout(progress_layout)
        main_layout.addLayout(imp_btn_layout)
        # Set main layout
        self.setLayout(main_layout)

        # Disable buttons and hide progress bar
        self.logoutButton.setEnabled(False)
        self.set_download_form_enabled(False)
        self.progressLabel.hide()
        self.progressBar.hide()

        self.loginField.setText(self.config['email'])
        if self.config['rememberPassword']:
            self.checkBoxSavePass.setChecked(True)
            self.passField.setText(self.config['password'])

        self.show()
        if self.config['stayLoggedIn']:
            self.passField.clearFocus()
            cookies_path = utils.get_cookies_path()
            self.authorize(self.loginField.text(), self.passField.text(), cookies_path)
        elif not self.config['rememberPassword']:
            # Have to set focus for typing after creating all widgets
            self.passField.setFocus()

        self.allow_to_close(True)

# Button clicks handlers and overridden events
###################################################

    def loginButtonClicked(self):
        self.allow_to_close(False)
        # Read login and password
        login = self.loginField.text()
        password = self.passField.text()

        self.config['email'] = login
        if self.checkBoxSavePass.checkState():
            self.config['password'] = password
            self.config['rememberPassword'] = True
        else:
            self.config['password'] = ''
            self.config['rememberPassword'] = False

        if self.checkBoxStayLoggedIn.checkState():
            self.config['stayLoggedIn'] = True
            cookies_path = utils.get_cookies_path()
            self.authorize(login, password, cookies_path)
        else:
            self.config['stayLoggedIn'] = False
            self.authorize(login, password)
        utils.update_config(self.config)

        self.allow_to_close(True)

    def logoutButtonClicked(self):
        # Disable logout and other buttons
        self.logoutButton.setEnabled(False)
        self.set_download_form_enabled(False)

        delattr(self, 'lingualeo')
        utils.clean_cookies()
        self.config['stayLoggedIn'] = False
        utils.update_config(self.config)

        # Enable Login button and fields
        self.set_login_form_enabled(True)
        self.allow_to_close(True)

    def importAllButtonClicked(self):
        # Disable buttons
        self.set_download_form_enabled(False)
        self.download_words()

    def wordsetButtonClicked(self):
        self.allow_to_close(False)
        wordsets = self.lingualeo.get_wordsets()
        if wordsets:
            self.set_download_form_enabled(False)
            wordset_window = WordsetsWindow(wordsets)
            wordset_window.Wordsets.connect(self.download_words)
            wordset_window.Cancel.connect(self.set_download_form_enabled)
            wordset_window.exec_()

    def reject(self):
        """
        Override reject event to handle Escape key press correctly
        """
        self.close()

    def closeEvent(self, event):
        """
        Override close event to safely close plugin
        """
        if hasattr(self, 'threadclass') and not self.threadclass.isFinished():
            qm = QMessageBox()
            answer = qm.question(self, '', "Are you sure you want to stop downloading?",
                                 qm.Yes | qm.Cancel, qm.Cancel)
            if answer == qm.Yes and not self.threadclass.isFinished():
                self.threadclass.terminate()
            elif answer == qm.Cancel:
                event.ignore()
                return
        # Delete attribute before closing to allow running the plugin again
        delattr(mw, 'lingualeoanki')
        if not self.checkBoxStayLoggedIn.checkState():
            utils.clean_cookies()
        mw.reset()

    def downloadFinished(self):
        if hasattr(self, 'wordsFinalCount'):
            showInfo("%d words from LinguaLeo have been processed" % self.wordsFinalCount)
            delattr(self, 'wordsFinalCount')
        self.set_download_form_enabled(True)
        self.logoutButton.setEnabled(True)
        self.progressLabel.hide()
        self.progressBar.hide()
        self.allow_to_close(True)
        mw.reset()

# Functions for connecting to lingualeo and downloading words
###########################################################

    def authorize(self, login, password, cookies_path=None):
        """
        Creates lingualeo object and connects to the website
        """
        self.lingualeo = connect.Lingualeo(login, password, cookies_path)
        self.lingualeo.Error.connect(self.showErrorMessage)
        if self.lingualeo.get_connection():
            # Disable login button and fields
            self.set_login_form_enabled(False)
            # Enable all other buttons
            self.logoutButton.setEnabled(True)
            self.set_download_form_enabled(True)

    def download_words(self, wordsets=None):
        # TODO: Run it inside the other thread to handle big dictionaries
        self.allow_to_close(False)
        words = self.lingualeo.get_words_to_add(wordsets)
        filtered = self.filter_words(words)
        if filtered:
            self.start_download_thread(filtered)
        else:
            progress = self.get_progress_type()
            msg = 'No %s words to download' % progress if progress != 'Any' else 'No words to download'
            self.showErrorMessage(msg)
            self.set_download_form_enabled(True)
            self.allow_to_close(True)

    def filter_words(self, words):
        """
        Eliminates unnecessary to download words.
        We need to do it in main thread by using signals and slots
        """
        word_progress = self.get_progress_type()
        if word_progress == 'Unstudied':
            words = [word for word in words if word.get('progress_percent') < 100]
        elif word_progress == 'Studied':
            words = [word for word in words if word.get('progress_percent') == 100]
        update = self.checkBoxUpdateNotes.checkState()
        if not update:
            # Exclude duplicates, if full update is not required
            words = [word for word in words if not utils.is_duplicate(word)]
        return words

    def start_download_thread(self, words):
        # Activate progress bar
        self.progressBar.setValue(0)
        self.progressBar.show()
        self.progressLabel.show()
        self.logoutButton.setEnabled(False)
        # TODO: Show numbers in progress bar

        # Set Anki Model
        self.set_model()

        # Start downloading
        self.threadclass = connect.Download(words)
        self.threadclass.start()
        self.threadclass.Length.connect(self.progressBar.setMaximum)
        self.threadclass.Word.connect(self.addWord)
        self.threadclass.Counter.connect(self.progressBar.setValue)
        self.threadclass.FinalCounter.connect(self.setFinalCount)
        self.threadclass.Error.connect(self.showErrorMessage)
        self.threadclass.finished.connect(self.downloadFinished)

    def set_model(self):
        self.model = utils.prepare_model(mw.col, utils.fields, styles.model_css)

    def addWord(self, word):
        """
        Note is an SQLite object in Anki so you need
        to fill it out inside the main thread
        """
        utils.add_word(word, self.model)

    def setFinalCount(self, counter):
        self.wordsFinalCount = counter

# UI helpers
#####################################

    def showErrorMessage(self, msg):
        showInfo(msg)
        mw.reset()

    def get_progress_type(self):
        progress = 'Any'
        if self.rbutton_studied.isChecked():
            progress = 'Studied'
        elif self.rbutton_unstudied.isChecked():
            progress = 'Unstudied'
        return progress

    def set_download_form_enabled(self, mode):
        """
        Set buttons either enabled or disabled
        :param mode: bool
        """
        self.importAllButton.setEnabled(mode)
        self.importByDictionaryButton.setEnabled(mode)
        self.rbutton_any.setEnabled(mode)
        self.rbutton_studied.setEnabled(mode)
        self.rbutton_unstudied.setEnabled(mode)
        self.checkBoxUpdateNotes.setEnabled(mode)

    def set_login_form_enabled(self, mode):
        """
        Set login elements either enabled or disabled
        :param mode: bool
        """
        self.loginButton.setEnabled(mode)
        self.loginField.setEnabled(mode)
        self.passField.setEnabled(mode)
        self.checkBoxStayLoggedIn.setEnabled(mode)
        self.checkBoxSavePass.setEnabled(mode)

    def allow_to_close(self, flag):
        """
        Sets attribute 'silentlyClose' to allow Anki's main window
        to automatically close plugin windows on exit
        :param flag: bool
        """
        if flag:
            setattr(self, 'silentlyClose', 1)
        elif hasattr(self, 'silentlyClose'):
            delattr(self, 'silentlyClose')


class WordsetsWindow(QDialog):
    Wordsets = pyqtSignal(list)
    Cancel = pyqtSignal(bool)

    def __init__(self, wordsets, parent=None):
        QDialog.__init__(self, parent)
        self.wordsets = wordsets
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Choose dictionaries to import')
        # Buttons and fields
        self.importButton = QPushButton("Import", self)
        self.cancelButton = QPushButton("Cancel", self)
        self.importButton.clicked.connect(self.importButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        key_name = 'Ctrl' if pm.system() == 'Windows' or pm.system() == 'Linux' else 'Cmd'
        label = QLabel('Hold %s to select several dictionaries' % key_name)
        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        for wordset in self.wordsets:
            item_name = wordset['name'] + ' (' + str(wordset['countWords']) + ' words in total)'
            item = QListWidgetItem(item_name)
            item.wordset_id = wordset['id']
            self.listWidget.addItem(item)

        # Horizontal layout for buttons
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.importButton)
        hbox.addWidget(self.cancelButton)
        hbox.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.listWidget)
        main_layout.addWidget(label)
        main_layout.addLayout(hbox)
        self.setLayout(main_layout)
        # Set attribute to allow Anki to close the plugin window
        setattr(self, 'silentlyClose', 1)
        self.show()

    def importButtonClicked(self):
        items = self.listWidget.selectedItems()
        selected_ids = []
        for item in items:
            selected_ids.append(str(item.wordset_id))
        selected_wordsets = []
        for wordset in self.wordsets:
            if str(wordset['id']) in selected_ids:
                selected_wordsets.append(wordset.copy())
        self.close()
        self.Wordsets.emit(selected_wordsets)

    def cancelButtonClicked(self):
        # Send signal to activate buttons and radio buttons on the main plugin window
        self.Cancel.emit(True)
        self.close()
