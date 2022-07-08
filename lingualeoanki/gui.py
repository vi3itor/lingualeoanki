import platform as pm

from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
# TODO: change to:  import connect as connector
from . import connect
from . import utils
from . import styles
from ._name import ADDON_NAME
from ._version import VERSION


# TODO: Make Russian localization
#  (since beginners are more comfortable with native language)

# TODO: Implement "Loading..." window to show user that list of words or list of dictionaries is being downloaded

class PluginWindow(QDialog):
    Authorize = pyqtSignal()
    RequestWords = pyqtSignal(str, list, bool)
    RequestWordsets = pyqtSignal(str)
    CheckVersion = pyqtSignal()
    StartDownload = pyqtSignal(list)

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.config = utils.get_config()
        self.is_active_download = False
        self.is_active_connection = False

        # Initialize UI
        ###############
        title = 'Import from LinguaLeo (version {})'.format(VERSION)
        self.setWindowTitle(title)
        if pm.system() == 'Windows':
            self.setWindowIcon(QIcon(os.path.join(utils.get_addon_dir(), 'favicon.ico')))

        # Login section widgets
        loginLabel = QLabel('Your LinguaLeo login:')
        self.loginField = QLineEdit()
        passLabel = QLabel('Your LinguaLeo password:')
        self.passField = QLineEdit()
        self.passField.setEchoMode(QLineEdit.EchoMode.Password)
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

        # Word status radio buttons
        self.status_button_group = QButtonGroup()
        self.rbutton_all = QRadioButton("Any")
        self.rbutton_new = QRadioButton("New")
        self.rbutton_learning = QRadioButton("Learning")
        self.rbutton_learned = QRadioButton("Learned")
        self.rbutton_all.setChecked(True)
        self.status_button_group.addButton(self.rbutton_all, 0)
        self.status_button_group.addButton(self.rbutton_new, 1)
        self.status_button_group.addButton(self.rbutton_learning, 2)
        self.status_button_group.addButton(self.rbutton_learned, 3)

        self.checkBoxUpdateNotes = QCheckBox('Update existing notes')
        self.progressLabel = QLabel('')
        self.progressBar = QProgressBar()

        self.api_label = QLabel('Choose API:')
        self.api_button_group = QButtonGroup()
        self.api_rbutton_new = QRadioButton('New (no context yet)')
        self.api_rbutton_old = QRadioButton('Old (with context)')
        self.api_rbutton_old.setEnabled(False)
        self.api_rbutton_new.setChecked(True)
        self.api_button_group.addButton(self.api_rbutton_new, 0)
        self.api_button_group.addButton(self.api_rbutton_old, 1)

        # TODO: Implement GUI element to ask what style cards to create:
        #  with typing correct answer or without (or use config for that purpose)

        # Login form layout
        login_form = QFormLayout()
        login_form.addRow(loginLabel, self.loginField)
        login_form.addRow(passLabel, self.passField)
        # Vertical layout for checkboxes
        login_checkboxes = QVBoxLayout()
        login_checkboxes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_checkboxes.addWidget(self.checkBoxStayLoggedIn)
        login_checkboxes.addWidget(self.checkBoxSavePass)
        # Horizontal layout for login buttons
        login_buttons = QHBoxLayout()
        # Add stretch to make buttons smaller
        login_buttons.addStretch()
        login_buttons.addWidget(self.loginButton)
        login_buttons.addWidget(self.logoutButton)
        login_buttons.addStretch()
        # Horizontal layout for API
        api_layout = QHBoxLayout()
        api_layout.addWidget(self.api_label)
        api_layout.addWidget(self.api_rbutton_new)
        api_layout.addWidget(self.api_rbutton_old)
        api_layout.addStretch()

        # Horizontal layout for radio buttons and update checkbox
        options_layout = QHBoxLayout()
        options_layout.addWidget(self.rbutton_all)
        options_layout.addWidget(self.rbutton_new)
        options_layout.addWidget(self.rbutton_learning)
        options_layout.addWidget(self.rbutton_learned)
        options_layout.addSpacing(15)
        options_layout.addWidget(self.checkBoxUpdateNotes)
        options_layout.addStretch()

        # Progress label and progress bar layout
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.progressLabel)
        progress_layout.addWidget(self.progressBar)

        # Form layout for option buttons and progress bar
        downloading_layout = QFormLayout()
        downloading_layout.addRow(api_layout)
        downloading_layout.addRow(options_layout)
        downloading_layout.addRow(progress_layout)
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
        main_layout.addLayout(downloading_layout)
        main_layout.addLayout(imp_btn_layout)
        # Set main layout
        self.setLayout(main_layout)

        # Disable buttons and hide progress bar
        self.logoutButton.setEnabled(False)
        self.set_download_form_enabled(False)
        self.progressBar.hide()

        self.loginField.setText(self.config['email'])
        if self.config['rememberPassword']:
            self.checkBoxSavePass.setChecked(True)
            self.passField.setText(self.config['password'])

        self.show()
        # Check for new version on disk and on github
        message = utils.get_version_update_notification()
        if message:
            showInfo(message)
            self.setWindowTitle(message)
        elif self.config['checkForNewVersion']:
            self.create_download_thread()
            self.CheckVersion.emit()

        if self.config['stayLoggedIn']:
            self.passField.clearFocus()
            cookies_path = utils.get_cookies_path()
            self.create_lingualeo_object(self.loginField.text(), self.passField.text(), cookies_path)
            self.Authorize.emit()
            self.show_progress_bar(True, "Connecting to Lingualeo...")
            # Disable login button and fields
            self.set_login_form_enabled(False)
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

        cookies_path = None
        if self.checkBoxStayLoggedIn.checkState():
            self.config['stayLoggedIn'] = True
            cookies_path = utils.get_cookies_path()
        else:
            self.config['stayLoggedIn'] = False

        self.create_lingualeo_object(login, password, cookies_path)
        self.Authorize.emit()
        self.show_progress_bar(True, 'Connecting to LinguaLeo...')
        # Disable login button and fields
        self.set_login_form_enabled(False)
        utils.update_config(self.config)

    def logoutButtonClicked(self):
        # Disable logout and other buttons
        self.logoutButton.setEnabled(False)
        self.set_download_form_enabled(False)

        utils.clean_cookies()
        self.config['stayLoggedIn'] = False
        utils.update_config(self.config)

        # Enable Login button and fields
        self.set_login_form_enabled(True)
        self.allow_to_close(True)

    def importAllButtonClicked(self):
        self.request_words([])

    def wordsetButtonClicked(self):
        self.set_elements_enabled(False)
        word_status = self.get_progress_status()
        self.RequestWordsets.emit(word_status)
        self.show_progress_bar(True, 'Requesting list of dictionaries...')

    def reject(self):
        """
        Override reject event to handle Escape key press correctly
        """
        self.close()

    def closeEvent(self, event):
        """
        Override close event to safely close add-on window
        """
        if self.is_active_download or self.is_active_connection:
            qm = QMessageBox()
            reason = 'downloading' if self.is_active_download else 'connecting to LinguaLeo'
            answer = qm.question(self, '', 'Are you sure you want to stop {}?'.format(reason),
                                 qm.Yes | qm.Cancel, qm.Cancel)
            if answer == qm.Cancel:
                event.ignore()
                return
            # TODO: Don't close add-on window if the 'Stop' button was pressed

        if hasattr(self, 'lingualeo_thread'):
            self.stop_thread(self.lingualeo_thread)
        if hasattr(self, 'download_thread'):
            self.stop_thread(self.download_thread)

        # Delete attribute before closing to allow running the add-on again
        if hasattr(mw, ADDON_NAME):
            delattr(mw, ADDON_NAME)
        if hasattr(self, 'checkBoxStayLoggedIn') and \
                not self.checkBoxStayLoggedIn.checkState():
            utils.clean_cookies()

    def stop_thread(self, thread):
        thread.quit()
        # Wait 5 seconds for thread to quit and terminate if needed
        if not thread.wait(5000):
            thread.terminate()

# Functions for connecting to LinguaLeo and downloading words
###########################################################
    def create_lingualeo_object(self, login, password, cookies_path=None):
        """
        Creates lingualeo object and moves it to the designated thread
        or disconnects existing object and creates a new one
        """
        if not hasattr(self, 'lingualeo_thread'):
            self.lingualeo_thread = QThread()
            self.lingualeo_thread.start()
        else:
            # Disconnect signals from slots
            self.lingualeo_thread.lingualeo.Error.disconnect(self.showErrorMessage)
            self.Authorize.disconnect(self.lingualeo_thread.lingualeo.authorize)
            self.lingualeo_thread.lingualeo.AuthorizationStatus.disconnect(self.process_authorization)
            self.lingualeo_thread.lingualeo.Words.disconnect(self.download_words)
            self.lingualeo_thread.lingualeo.Wordsets.disconnect(self.process_wordsets)
            self.lingualeo_thread.lingualeo.Busy.disconnect(self.set_busy_connecting)
            self.RequestWords.disconnect(self.lingualeo_thread.lingualeo.get_words_to_add)
            self.RequestWordsets.disconnect(self.lingualeo_thread.lingualeo.get_wordsets)
            # Delete previous LinguaLeo object
            # TODO: Investigate if it should be done differently
            self.lingualeo_thread.lingualeo.deleteLater()
        lingualeo = connect.Lingualeo(login, password, cookies_path)
        lingualeo.moveToThread(self.lingualeo_thread)
        lingualeo.Error.connect(self.showErrorMessage)
        self.Authorize.connect(lingualeo.authorize)
        lingualeo.AuthorizationStatus.connect(self.process_authorization)
        lingualeo.Words.connect(self.download_words)
        lingualeo.Wordsets.connect(self.process_wordsets)
        lingualeo.Busy.connect(self.set_busy_connecting)
        self.RequestWords.connect(lingualeo.get_words_to_add)
        self.RequestWordsets.connect(lingualeo.get_wordsets)
        self.lingualeo_thread.lingualeo = lingualeo

    @pyqtSlot(bool)
    def process_authorization(self, status):
        if status:
            self.set_elements_enabled(True)
        else:
            utils.clean_cookies()
            self.set_login_form_enabled(True)
            self.allow_to_close(True)
        self.show_progress_bar(False, '')

    @pyqtSlot(list)
    def process_wordsets(self, wordsets):
        self.show_progress_bar(False, '')
        if wordsets:
            wordset_window = WordsetsWindow(wordsets)
            wordset_window.SelectedWordsets.connect(self.request_words)
            wordset_window.Cancel.connect(self.set_elements_enabled)
            wordset_window.Cancel.connect(self.activate_addon_window)
            wordset_window.exec()
        else:
            self.set_elements_enabled(True)

    def request_words(self, wordsets):
        self.activate_addon_window()
        self.set_elements_enabled(False)
        # TODO: Change 'Exit' Button label to 'Stop' and back
        status = self.get_progress_status()
        with_context = self.api_rbutton_old.isChecked()
        self.RequestWords.emit(status, wordsets, with_context)
        self.show_progress_bar(True, 'Requesting list of words...')

    @pyqtSlot(list)
    def download_words(self, words):
        self.show_progress_bar(True, 'Found {} words. Excluding already existing...'.format(len(words)))
        self.update()
        filtered = self.filter_words(words) if not self.checkBoxUpdateNotes.isChecked() else words
        if filtered:
            self.start_downloading_media(filtered)
        else:
            progress = self.get_progress_status()
            msg = 'No %s words to download' % progress if progress != 'all' else 'No words to download'
            showInfo(msg)
            self.show_progress_bar(False, '')
            self.allow_to_close(True)
            self.logoutButton.setEnabled(True)
            self.set_download_form_enabled(True)
            self.activate_addon_window()

    def filter_words(self, words):
        """
        Eliminates unnecessary to download words.
        We have to do it in main thread to query database for duplicates
        """
        if not words:
            return None
        # Exclude duplicates
        words = [word for word in words if not utils.is_duplicate(word.get('wordValue'))]
        return words

    def start_downloading_media(self, words):
        # Activate progress bar
        label = 'Downloading media for {} words...'.format(len(words))
        self.show_progress_bar(True, label, len(words))
        # Set Anki Model
        if not hasattr(self, 'model'):
            self.model = utils.prepare_model(mw.col, utils.fields, styles.model_css)

        # Create and start a thread if it is a first run
        self.create_download_thread()
        # Start downloading
        self.StartDownload.emit(words)

    def create_download_thread(self):
        if hasattr(self, 'download_thread'):
            return
        self.download_thread = QThread()
        downloader = connect.Download()
        downloader.moveToThread(self.download_thread)
        downloader.Word.connect(self.add_word)
        downloader.Counter.connect(self.progressBar.setValue)
        downloader.FinalCounter.connect(self.download_finished)
        downloader.Message.connect(self.showErrorMessage)
        downloader.Busy.connect(self.set_busy_download)
        self.CheckVersion.connect(downloader.check_for_new_version)
        self.StartDownload.connect(downloader.add_separately)
        self.download_thread.downloader = downloader
        self.download_thread.start()

    def download_finished(self, final_count):
        message = 'words have' if final_count != 1 else 'word has'
        showInfo("{} {} been imported".format(final_count, message))
        self.set_elements_enabled(True)
        self.show_progress_bar(False, '')

    def add_word(self, word):
        """
        Note is an SQLite object in Anki so you need
        to fill it out inside the main thread
        """
        utils.add_word(word, self.model)

    @pyqtSlot(bool)
    def set_busy_download(self, status):
        """
        When downloading media for words
        """
        self.is_active_download = status

    @pyqtSlot(bool)
    def set_busy_connecting(self, status):
        """
        When connecting to LinguaLeo for authorization or requesting list of words or wordsets
        """
        self.is_active_connection = status

# UI helpers
#####################################
    def show_progress_bar(self, mode, label, max_range=0):
        if mode:
            self.progressBar.setRange(0, max_range)
            self.progressBar.setValue(0)  # is it required?
            self.progressBar.show()
        else:
            self.progressBar.hide()
        self.progressLabel.setText(label)

    def showErrorMessage(self, msg):
        showInfo(msg)

    def set_elements_enabled(self, mode):
        """
        Enables or disables download form, logout button,
        and allows or disallows closing the addon silently
        """
        self.set_download_form_enabled(mode)
        self.logoutButton.setEnabled(mode)
        self.allow_to_close(mode)

    def get_progress_status(self):
        progress = 'all'
        if self.rbutton_learned.isChecked():
            progress = 'learned'
        elif self.rbutton_learning.isChecked():
            progress = 'learning'
        elif self.rbutton_new.isChecked():
            progress = 'new'
        return progress

    def set_download_form_enabled(self, mode):
        """
        Set buttons either enabled or disabled
        :param mode: bool
        """
        self.importAllButton.setEnabled(mode)
        self.importByDictionaryButton.setEnabled(mode)
        self.rbutton_all.setEnabled(mode)
        self.rbutton_new.setEnabled(mode)
        self.rbutton_learning.setEnabled(mode)
        self.rbutton_learned.setEnabled(mode)
        self.checkBoxUpdateNotes.setEnabled(mode)
        self.api_rbutton_new.setEnabled(mode)
        # self.api_rbutton_old.setEnabled(mode)
        self.update()

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
        self.update()

    def activate_addon_window(self, optional=True):
        addon_window = getattr(mw, ADDON_NAME, None)
        if addon_window:
            addon_window.activateWindow()
            addon_window.raise_()

    def allow_to_close(self, flag):
        """
        Sets attribute 'silentlyClose' to allow Anki's main window
        to automatically close add-on windows on exit
        :param flag: bool
        """
        if flag:
            setattr(self, 'silentlyClose', 1)
        elif hasattr(self, 'silentlyClose'):
            delattr(self, 'silentlyClose')


class WordsetsWindow(QDialog):
    SelectedWordsets = pyqtSignal(list)
    Cancel = pyqtSignal(bool)

    def __init__(self, wordsets, parent=None):
        QDialog.__init__(self, parent)
        self.wordsets = wordsets
        self.setWindowTitle('Choose dictionaries to import')
        if pm.system() == 'Windows':
            self.setWindowIcon(QIcon(os.path.join(utils.get_addon_dir(), 'dict.ico')))

        # Buttons and fields
        self.importButton = QPushButton("Import", self)
        self.cancelButton = QPushButton("Cancel", self)
        self.importButton.clicked.connect(self.importButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        key_name = 'Ctrl' if pm.system() == 'Windows' or pm.system() == 'Linux' else 'Cmd'
        label = QLabel('Hold %s to select several dictionaries' % key_name)
        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        for wordset in self.wordsets:
            item = QListWidgetItem(wordset['list_name'])
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
        # Set attribute to allow Anki to close the add-on window
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
                selected_wordsets.append(wordset['id'])
        self.close()
        self.SelectedWordsets.emit(selected_wordsets)

    def cancelButtonClicked(self):
        # Send signal to activate buttons and radio buttons on the main add-on window
        self.Cancel.emit(True)
        self.close()
