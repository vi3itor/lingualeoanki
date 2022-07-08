import os
from .six.moves import http_cookiejar
from .six.moves import urllib
import socket
import json
import ssl
import base64

from aqt.qt import *
from . import utils


class Lingualeo(QObject):
    Busy = pyqtSignal(bool)
    Error = pyqtSignal(str)
    AuthorizationStatus = pyqtSignal(bool)
    Words = pyqtSignal(list)
    Wordsets = pyqtSignal(list)

    def __init__(self, email, password, cookies_path=None, parent=None):
        QObject.__init__(self, parent)
        self.email = email
        self.password = password
        self.cj = http_cookiejar.MozillaCookieJar()
        if cookies_path:
            self.cookies_path = cookies_path
            if not os.path.exists(cookies_path):
                self.save_cookies()
            else:
                try:
                    self.cj.load(cookies_path)
                except (IOError, TypeError, ValueError):
                    # TODO: process exceptions separately
                    self.cj = http_cookiejar.MozillaCookieJar()
                except:
                    # TODO: Handle corrupt cookies loading
                    self.cj = http_cookiejar.MozillaCookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        config = utils.get_config()
        self.WORDS_PER_REQUEST = config['wordsPerRequest'] if config else 999
        self.url_prefix = 'https://'
        self.msg = ''
        self.tried_ssl_fix = False

    @pyqtSlot()
    def authorize(self):
        self.Busy.emit(True)
        self.AuthorizationStatus.emit(self.get_connection())
        self.Busy.emit(False)

    def get_connection(self):
        """Make sure that user is authorized and activated the supported language pair."""
        # TODO: rewrite the method, unify handling of the exceptions
        try:
            if not self.is_authorized():
                status = self.auth()
                if status.get('error_msg'):
                    self.msg = status['error_msg']
        except urllib.error.HTTPError:
            self.msg = "We got HTTP Error. Probably API has been changed (again). " \
                       "Please try again. If error persists, please copy the error message and create a new issue " \
                       "on GitHub (https://github.com/vi3itor/lingualeoanki/issues/new)."
        except (urllib.error.URLError, socket.error) as e:
            # TODO: Find better (secure) fix
            """
            SSLError was noticed on MacOS, because Python 3.6m used in Anki doesn't have 
            security certificates downloaded. The easiest (but unsecure) way is to create SSL context.
            """
            if 'SSL' in str(e) and not self.tried_ssl_fix:
                # Problem with https connection, trying ssl fix
                https_handler = urllib.request.HTTPSHandler(context=ssl._create_unverified_context())
                self.opener = urllib.request.build_opener(https_handler, urllib.request.HTTPCookieProcessor(self.cj))
                self.tried_ssl_fix = True
                return self.get_connection()
            else:
                self.msg = "Can't authorize. Problems with internet connection. Error message: " + str(e)
        except ValueError:
            self.msg = "Error! Possibly, invalid data was received from LinguaLeo"
        except Exception as e:
            self.msg = "There's been an unexpected error. Please copy the error message and create a new issue " \
                       "on GitHub (https://github.com/vi3itor/lingualeoanki/issues/new). Error: " + str(e)
        # TODO: Refactor, use msg instead of self.msg
        if self.msg:
            self.Error.emit(self.msg)
            self.msg = ''
            return False
        # Check for supported language pair
        return self.confirm_language_pair()

    def confirm_language_pair(self):
        """Verify that user activated a supporting language pair in the profile"""
        user_info = self.get_user_profile()
        if not user_info:
            return False
        if not (user_info["nativeLang"] == "ru" and user_info["targetLang"] == "en"):
            msg = 'Only English-Russian mode is currently supported. Please go to lingualeo.com, select English to ' \
                  'study and try again. Other languages may be supported in the future. If you still have any ' \
                  'problems please open a new issue on GitHub (https://github.com/vi3itor/lingualeoanki/issues/new)'
            self.Error.emit(msg)
            return False
        return True

    def get_user_profile(self):
        """
        Use LinguaLeo API to get user profile information.
        """
        url = 'api.lingualeo.com/ProcessTraining'
        values = {"apiVersion": "1.1.0", "trainingName": "getUserStatus"}
        msg, exc_msg = '', ''
        try:
            response = self.get_content(url, values)
            status = response.get('status', '')
            if status == 'error':
                msg = response['error']['message']
            elif status == 'ok' and response['data'] and response["data"]["nativeLang"] and response["data"]["targetLang"]:
                return response['data']
        except Exception as e:
            exc_msg = str(e)
        msg = "There's been an unexpected error when requesting user profile information. Please copy the error message and create a new issue " \
              "on GitHub (https://github.com/vi3itor/lingualeoanki/issues/new). Error: " + (msg if msg else exc_msg)
        self.Error.emit(msg)
        return None

    @pyqtSlot(str)
    def get_wordsets(self, status):
        """
        Get user's dictionaries (wordsets), including default ones,
        and return ids and names of not empty ones
        """
        # TODO: Unite exception processing for get_wordsets and get_words_to_add into one function (e.g. get_data),
        #  it will make code cleaner and reduce errors
        self.Busy.emit(True)
        wordsets = []
        if not self.get_connection():
            self.Wordsets.emit(wordsets)
            self.Busy.emit(False)
            return
        url = 'api.lingualeo.com/GetWordSets'
        values = {'apiVersion': '1.0.0',
                  'request': [{'subOp': 'myAll', 'type': 'user', 'perPage': 999,
                               'attrList': WORDSETS_ATTRIBUTE_LIST, 'sortBy': 'created'}],
                  'ctx': {'config': {'isCheckData': True, 'isLogging': True}}}
        try:
            response = self.get_content(url, values)
            if response.get('error') or not response.get('data'):
                raise Exception('Incorrect data received from LinguaLeo. Possibly API was changed again. '
                                + response.get('error').get('message'))
            all_wordsets = response['data'][0]['items']
            # Add only non-empty dictionaries
            for wordset in all_wordsets:
                count = wordset['countWordsLearned'] if status == 'learned' else wordset['countWords']
                if count == 0:
                    continue  # No need to show an empty dictionary in the list
                # To avoid unicode string error on Python 2.7, it should be set in the following way
                list_name = wordset['name'] + ' ({} {})'.format(count, 'words' if count > 1 else 'word')
                if wordset['id'] == 1 and status != 'learned':  # Main dictionary with all words
                    list_name = list_name[:-1] + ' in total)'
                wordsets.append({'list_name': list_name, 'id': wordset['id']})
            self.save_cookies()
            if not wordsets:
                self.msg = 'No user dictionaries found'
        except (urllib.error.URLError, socket.error):
            self.msg = "Can't get dictionaries. Problem with internet connection."
        except ValueError:
            self.msg = "Error! Possibly, invalid data was received from LinguaLeo."
        except KeyError:
            self.msg = "Can't get list of wordsets. Possibly API was changed again. Please create a new issue " \
                       "on GitHub: https://github.com/vi3itor/lingualeoanki/issues/new"
        except Exception as e:
            self.msg = "There's been an unexpected error. Please copy the error message and create a new issue " \
                       "on GitHub (https://github.com/vi3itor/lingualeoanki/issues/new). Error: " + str(e)
        if self.msg:
            self.Error.emit(self.msg)
            self.msg = ''
            wordsets = []

        self.Wordsets.emit(wordsets)
        self.Busy.emit(False)

    @pyqtSlot(str, list, bool)
    def get_words_to_add(self, status, wordsets, with_context=False):
        self.Busy.emit(True)
        words = []
        unique_word_ids = set()
        if not self.get_connection():
            self.Words.emit(words)
            self.Busy.emit(False)
            return
        try:
            get_func = self.get_words_with_context if with_context else self.get_words
            wordset_ids = wordsets if wordsets else [1]
            for wordset_id in wordset_ids:
                received_words = get_func(status, wordset_id)
                # print(get_func.__name__ + ' ' + str(len(received_words)) + ' words received')
                for word in received_words:
                    if word['id'] not in unique_word_ids:
                        words.append(word)
                        unique_word_ids.add(word['id'])
            # TODO: Notify user if len(unique_words) is less than a number of words in the main wordset

            self.save_cookies()
        except (urllib.error.URLError, socket.error):
            self.msg = "Can't download words. Problem with internet connection."
        except ValueError:
            self.msg = "Error! Possibly, invalid data was received from LinguaLeo"
        except KeyError:
            self.msg = "Can't get list of words. Possibly API was changed again. Please create a new issue " \
                       "on GitHub: https://github.com/vi3itor/lingualeoanki/issues/new"
        except Exception as e:
            self.msg = "There's been an unexpected error. Please copy the error message and create a new issue " \
                       "on GitHub (https://github.com/vi3itor/lingualeoanki/issues/new). Error: " + str(e)
        if self.msg:
            self.Error.emit(self.msg)
            self.msg = ''
            # TODO: Check if it is handled correctly (avoid double Info window)
            words = []

        self.Words.emit(words)
        self.Busy.emit(False)

    def get_words(self, status, wordset_id):
        """
        Get words either from main ('my') vocabulary or from user's dictionaries (wordsets)
        Response data consists of word groups that are separated by date.
        Each word group has:
        groupCount - number of words in the group,
        groupName - name of the group, like 'new' or 'year_2' (stands for 2 years ago),
        words - list of words (not more than self.WORDS_PER_REQUEST)
        :param status: progress status of the word: 'all', 'new', 'learning', 'learned'
        :param wordset_id: an id of the wordset (1 - for main dictionary with all words)
        :return: list of words, where each word is a dict
        """
        url = 'api.lingualeo.com/GetWords'
        date_group = 'start'
        offset = {}
        values = {"apiVersion": "1.0.1", "attrList": WORDS_ATTRIBUTE_LIST,
                  "category": "", "dateGroup": date_group, "mode": "basic", "perPage": self.WORDS_PER_REQUEST,
                  "status": status, "offset": offset, "search": "", "training": None, "wordSetId": wordset_id,
                  "ctx": {"config": {"isCheckData": True, "isLogging": True}}}

        words = []
        words_received = 0
        extra_date_group = date_group  # to get into the while loop

        # TODO: Refactor while loop (e.g. request words from each group until it is not empty)
        # Request the words until
        while words_received > 0 or extra_date_group:
            if words_received == 0 and extra_date_group:
                values['dateGroup'] = extra_date_group
                extra_date_group = None
            else:
                values['dateGroup'] = date_group
                values['offset'] = offset
            response = self.get_content(url, values)
            word_groups = response.get('data')
            if response.get('error'):
                raise Exception('Incorrect data received from LinguaLeo. Possibly API has been changed again. '
                                + response.get('error'))
            words_received = 0
            for word_group in word_groups:
                word_chunk = word_group.get('words')
                if word_chunk:
                    words += word_chunk
                    words_received += len(word_chunk)
                    date_group = word_group.get('groupName')
                    offset['wordId'] = word_group.get('words')[-1].get('id')
                elif words_received > 0:
                    ''' 
                    If the next word_chunk is empty, and we completed the previous, 
                    next response should be to the next group
                    '''
                    if words_received < self.WORDS_PER_REQUEST:
                        date_group = word_group.get('groupName')
                        extra_date_group = None
                        offset = {}
                    else:  # words_received == self.WORDS_PER_REQUEST
                        '''We either need to continue with this group or try the next'''
                        extra_date_group = word_group.get('groupName')
                    break
        return words

    def get_words_with_context(self, status, wordset_id):
        """
        This temporary function is to support old API until LinguaLeo fixes all issues with new API:
        currently some words aren't seen in the Web interface (and can't be downloaded with call to new API)
        and it's not possible to get context for the words at once using new API yet.
        :param status: progress status of the word: 'all', 'new', 'learning', 'learned'
        :param wordset_id: id of only one wordset represented as list (e.g., [1] to download from main dictionary)
        :return: list of words, where each word is a dict
        """
        # TODO: Unite get_words and get_words_old_api functions into one
        url = 'api.lingualeo.com/GetWords'
        values = {"apiVersion": "1.0.0", "attrList": WORDS_ATTRIBUTE_LIST,
                  "category": "", "mode": "basic", "perPage": self.WORDS_PER_REQUEST, "status": status,
                  "wordSetIds": [wordset_id], "offset": None, "search": "", "training": None,
                  "ctx": {"config": {"isCheckData": True, "isLogging": True}}}

        words = []
        next_chunk = self.get_content(url, values).get('data')
        # Continue getting the words until list is not empty
        while next_chunk:
            words += next_chunk
            values['offset'] = {'wordId': next_chunk[-1].get('id')}
            next_chunk = self.get_content(url, values).get('data')

        return words

    def save_cookies(self):
        if hasattr(self, 'cookies_path'):
            self.cj.save(self.cookies_path)

    # Low level methods
    #########################

    def auth(self):
        url = 'lingualeo.com/api/auth'
        values = {
            "type": "mixed",
            "credentials": {"email": self.email, "password": self.password}
        }
        # Without this header request gets Error 405: Not Allowed
        extra_headers = {'Referer': 'https://lingualeo.com/ru/'}
        content = self.get_content(url, values, extra_headers)
        # Fun fact: if user enters incorrect email, LinguaLeo will create a new account!
        self.save_cookies()
        return content

    def is_authorized(self):
        url = 'api.lingualeo.com/isauthorized'
        full_url = self.url_prefix + url
        response = self.opener.open(full_url)
        status = json.loads(response.read()).get('is_authorized', False)
        return status

    def get_content(self, url, values, more_headers=None):
        """
        A method to request content using new API
        :param url:
        :param values: json
        :param more_headers: dic
        :return: json
        """
        full_url = self.url_prefix + url
        data = json.dumps(values)
        data = data.encode("utf-8")

        headers = {'Content-Type': 'application/json'}
        if more_headers:
            headers.update(more_headers)
        # We have to create a request object, because urllibopener won't change default headers
        req = urllib.request.Request(full_url, data, headers)
        req.add_header('User-Agent', 'Anki Add-on')

        response = self.opener.open(req)
        return json.loads(response.read())

    """
    Using requests module (only in Anki 2.1) it can be performed as:

    def requests_get_content(self, url, data):
        full_url = self.url_prefix + url
        headers = {'Content-Type': 'text/plain'}
        r = requests.post(full_url, json=data, headers=headers)
        # print(r.status_code)
        return r.json()
    """
    # TODO: Add processing of http status codes in exceptions,
    #  see: http://docs.python-requests.org/en/master/user/quickstart/#response-status-codes


class Download(QObject):
    Busy = pyqtSignal(bool)
    Counter = pyqtSignal(int)
    FinalCounter = pyqtSignal(int)
    Word = pyqtSignal(dict)
    Message = pyqtSignal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        config = utils.get_config()
        self.timeout = config['downloadTimeout']
        self.retries = config['numberOfRetries']
        self.sleep_seconds = config['sleepSeconds']
        self.threadpool = QThreadPool(self)
        max_parallel_downloads = 3
        max_threads = config['parallelDownloads']
        parallel_downloads = min(max_threads, max_parallel_downloads)
        self.threadpool.setMaxThreadCount(parallel_downloads)
        self.problem_words = []
        self.counter = 0
        self.total_words = 0

    @pyqtSlot(list)
    def add_separately(self, words):
        """
        Divides downloading and filling note to different threads
        because you cannot create SQLite objects outside the main
        thread in Anki. Also you cannot download files in the main
        thread because it will freeze GUI
        """
        self.counter = 0
        self.total_words = len(words)
        self.Busy.emit(True)

        for word in words:
            download_worker = DownloadWorker(word, self.timeout, self.retries, self.sleep_seconds)
            download_worker.signals.Word.connect(self.emit_word_and_counter)
            download_worker.signals.ProblemWord.connect(self.problem_words.append)
            # print('Adding worker for ' + word['wordValue'])
            self.threadpool.start(download_worker)

    @pyqtSlot(dict)
    def emit_word_and_counter(self, word):
        self.Word.emit(word)
        self.counter += 1
        # print("Counter " + str(self.counter))
        self.Counter.emit(self.counter)
        if self.counter == self.total_words:
            if self.problem_words:
                self.emit_problem_words_msg()
            self.FinalCounter.emit(self.counter)
            self.Busy.emit(False)

    def emit_problem_words_msg(self):
        error_msg = ("We weren't able to download media for these "
                     "words because of broken links in LinguaLeo "
                     "or problems with an internet connection: ")
        for problem_word in self.problem_words[:-1]:
            error_msg += problem_word + ', '
        error_msg += self.problem_words[-1] + '.'
        self.Message.emit(error_msg)
        self.problem_words = []

    @pyqtSlot()
    def check_for_new_version(self):
        # Older anki clients (< 2.1.23 shouldn't check for new versions of the add-on)
        if utils.anki_version < 23:
            return
        # TODO: Investigate if it is better to call Anki's internal mechanism to check for new versions?
        self.Busy.emit(True)
        url = 'https://api.github.com/repos/vi3itor/lingualeoanki/contents/lingualeoanki/_version.py'
        try:
            # TODO: Find more secure fix
            resp = urllib.request.urlopen(url, context=ssl._create_unverified_context())
            resp = json.loads(resp.read())
            github_file = base64.b64decode(resp['content']).decode('utf-8').split('\n')
            if utils.is_newer_version_available(github_file):
                self.Message.emit('Warning! A new version of Add-on is available. Please consider updating!')
        except:
            # TODO: Handle connection exception
            pass
        self.Busy.emit(False)


class DownloadWorker(QRunnable):
    def __init__(self, word, timeout, retries, sleep_seconds):
        QRunnable.__init__(self)
        self.word = word
        self.timeout = timeout
        self.retries = retries
        self.sleep_seconds = sleep_seconds
        self.signals = WorkerSignals()

    def run(self):
        try:
            # print('Downloading media for ' + self.word['wordValue'] + ' just started')
            utils.send_to_download(self.word, self.timeout, self.retries, self.sleep_seconds)
        except (urllib.error.URLError, socket.error):
            # print("Problem with " + self.word['wordValue'])
            self.signals.ProblemWord.emit(self.word.get('wordValue'))
        # print('Worker for ' + self.word['wordValue'] + ' finished')
        self.signals.Word.emit(self.word)


class WorkerSignals(QObject):
    """
    Defines the signals for a worker thread.
    """
    Word = pyqtSignal(dict)
    ProblemWord = pyqtSignal(str)


# New API requires list of attributes
WORDS_ATTRIBUTE_LIST = {"id": "id", "wordValue": "wd", "origin": "wo", "wordType": "wt",
                        "translations": "trs", "wordSets": "ws", "created": "cd",
                        "learningStatus": "ls", "progress": "pi", "transcription": "scr",
                        "pronunciation": "pron", "relatedWords": "rw", "association": "as",
                        "trainings": "trainings", "listWordSets": "listWordSets",
                        "combinedTranslation": "trc", "picture": "pic", "speechPartId": "pid",
                        "wordLemmaId": "lid", "wordLemmaValue": "lwd"}

WORDSETS_ATTRIBUTE_LIST = {"type": "type", "id": "id", "name": "name", "countWords": "cw",
                           "countWordsLearned": "cl", "wordSetId": "wordSetId", "picture": "pic",
                           "category": "cat", "status": "st", "source": "src"}
