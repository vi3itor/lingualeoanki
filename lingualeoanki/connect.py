import os
from .six.moves import http_cookiejar
from .six.moves import urllib
import socket
import json
import ssl

from aqt.qt import *
from . import utils


class Lingualeo(QObject):
    Error = pyqtSignal(str)

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
        self.url_prefix = 'https://'
        self.msg = ''
        self.tried_ssl_fix = False

    def get_connection(self):
        try:
            if not self.is_authorized():
                status = self.auth()
                if status.get('error_msg'):
                    self.msg = status['error_msg']
        except (urllib.error.URLError, socket.error) as e:
            # TODO: Find better (secure) fix
            """
            SSLError was noticed on MacOS, because Python 3.6m used in Anki doesn't have 
            security certificates downloaded. The easiest (but unsecure) way is to create SSL context.
            """
            if 'SSL' in str(e.args) and not self.tried_ssl_fix:
                # Problem with https connection, trying ssl fix
                https_handler = urllib.request.HTTPSHandler(context=ssl._create_unverified_context())
                self.opener = urllib.request.build_opener(https_handler, urllib.request.HTTPCookieProcessor(self.cj))
                self.tried_ssl_fix = True
                return self.get_connection()
            else:
                self.msg = "Can't authorize. Problems with internet connection. Error message: " + str(e.args)
        except ValueError:
            self.msg = "Error! Possibly, invalid data was received from LinguaLeo"
        except Exception as e:
            self.msg = "There's been an unexpected error. Please copy the error message and create a new issue " \
                       "on GitHub (https://github.com/vi3itor/lingualeoanki/issues/new). Error: " + str(e.args)
        if self.msg:
            self.Error.emit(self.msg)
            self.msg = ''
            return False
        return True

    def get_wordsets(self):
        """
        Get user's dictionaries (wordsets), including default ones,
        and return those, that are not empty
        """
        if not self.get_connection():
            return None
        try:
            url = 'api.lingualeo.com/GetWordSets'
            values = {'apiVersion': '1.0.0',
                      'request': [{'subOp': 'myAll', 'type': 'user', 'perPage': 999,
                                   'attrList': WORDSETS_ATTRIBUTE_LIST, 'sortBy': 'created'}],
                      'ctx': {'config': {'isCheckData': True, 'isLogging': True}}}
            headers = {'Content-Type': 'application/json'}
            json_data = json.dumps(values)
            response = self.get_content(url, json_data, headers)
            if response.get('error') or not response.get('data'):
                raise Exception('Incorrect data received from LinguaLeo. Possibly API has been changed again. '
                                + response.get('error').get('message'))
            all_wordsets = response['data'][0]['items']
            wordsets = []
            # Add only non-empty dictionaries
            for wordset in all_wordsets:
                if wordset.get('countWords') and wordset['countWords'] != 0:
                    wordsets.append(wordset.copy())
            self.save_cookies()
            if not wordsets:
                self.msg = 'No user dictionaries found'
        except (urllib.error.URLError, socket.error):
            self.msg = "Can't get dictionaries. Problem with internet connection."
        except ValueError:
            self.msg = "Error! Possibly, invalid data was received from LinguaLeo"
        except Exception as e:
            self.msg = "There's been an unexpected error. Please copy the error message and create a new issue " \
                       "on GitHub (https://github.com/vi3itor/lingualeoanki/issues/new). Error: " + str(e.args)
        if self.msg:
            self.Error.emit(self.msg)
            self.msg = ''
            return None
        return wordsets

    def get_words_to_add(self, status, wordsets=None):
        if not self.get_connection():
            return None
        words = []
        try:
            if not wordsets:
                words = self.get_words(status, None)
            else:
                for wordset in wordsets:
                    received_words = self.get_words(status, wordset)
                    for word in received_words:
                        if is_word_unique(word, words):
                            words.append(word)
            self.save_cookies()
        except (urllib.error.URLError, socket.error):
            self.msg = "Can't download words. Problem with internet connection."
        except ValueError:
            self.msg = "Error! Possibly, invalid data was received from LinguaLeo"
        except Exception as e:
            self.msg = "There's been an unexpected error. Please copy the error message and create a new issue " \
                       "on GitHub (https://github.com/vi3itor/lingualeoanki/issues/new). Error: " + str(e.args)
        if self.msg:
            self.Error.emit(self.msg)
            self.msg = ''
            return None

        return words

    def get_words(self, status, wordset):
        """
        Get words either from main ('my') vocabulary or from user's dictionaries (wordsets)
        Response data consists of word groups that are separated by date.
        Each word group has:
        groupCount - number of words in the group,
        groupName - name of the group, like 'new' or 'year_2' (stands for 2 years ago),
        words - list of words (not more than PER_PAGE)
        :param status: progress status of the word: 'all', 'new', 'learning', 'learned'
        :param wordset: A wordset, or None to download all words (from main dictionary)
        :return: list of words, where each word is a dict
        """
        url = 'api.lingualeo.com/GetWords'
        headers = {'Content-Type': 'application/json'}
        # TODO: Move parameter to config?
        PER_PAGE = 100
        date_group = 'start'
        offset = {}
        values = {"apiVersion": "1.0.1", "attrList": WORDS_ATTRIBUTE_LIST,
                  "category": "", "dateGroup": date_group, "mode": "basic", "perPage": PER_PAGE, "status": status,
                  "wordSetId": wordset.get('id') if wordset else 1,  # ID of the main dictionary is 1
                  "offset": offset, "search": "", "training": None,
                  "ctx": {"config": {"isCheckData": True, "isLogging": True}}}

        words = []
        words_received = 0
        extra_date_group = date_group  # to get into the while loop

        # TODO: Refactor while loop below?
        # Request the words until
        while words_received > 0 or extra_date_group:
            if words_received == 0 and extra_date_group:
                values['dateGroup'] = extra_date_group
                extra_date_group = None
            else:
                values['dateGroup'] = date_group
                values['offset'] = offset
            json_data = json.dumps(values)
            response = self.get_content(url, json_data, headers)
            word_groups = response.get('data')
            if response.get('error') or not word_groups:
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
                    if words_received < PER_PAGE:
                        date_group = word_group.get('groupName')
                        extra_date_group = None
                        offset = {}
                    else:  # words_received == PER_PAGE
                        '''We either need to continue with this group or try the next'''
                        extra_date_group = word_group.get('groupName')
                    break
        return words

    def save_cookies(self):
        if hasattr(self, 'cookies_path'):
            self.cj.save(self.cookies_path)

    # Low level methods
    #########################

    def auth(self):
        url = 'lingualeo.com/ru/uauth/dispatch'
        values = {'email': self.email, 'password': self.password}
        data = urllib.parse.urlencode(values)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        content = self.get_content(url, data, headers)
        self.save_cookies()
        return content

    def is_authorized(self):
        url = 'api.lingualeo.com/api/isauthorized'
        full_url = self.url_prefix + url
        response = self.opener.open(full_url)
        status = json.loads(response.read()).get('is_authorized')
        return status

    def get_content(self, url, data, headers):
        """
        A method to request content using new API
        :param url:
        :param data: either json or urlencoded data
        :param headers: dic
        :return: json
        """
        full_url = self.url_prefix + url
        data = data.encode("utf-8")

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


def is_word_unique(check_word, words):
    """
    Helper function to test if a check_word doesn't appear in the list of words.
    Used for filtering out repeating words while downloading from multiple wordsets.
    :param check_word: dict
    :param words: list of dict
    :return: bool
    """
    for word in words:
        if word['id'] == check_word['id']:
            return False
    return True


class Download(QThread):
    Length = pyqtSignal(int)
    Counter = pyqtSignal(int)
    FinalCounter = pyqtSignal(int)
    Word = pyqtSignal(dict)
    Error = pyqtSignal(str)

    def __init__(self, words, parent=None):
        QThread.__init__(self, parent)
        self.words = words

    def run(self):
        self.Length.emit(len(self.words))
        self.add_separately()

    def add_separately(self):
        """
        Divides downloading and filling note to different threads
        because you cannot create SQLite objects outside the main
        thread in Anki. Also you cannot download files in the main
        thread because it will freeze GUI
        """
        counter = 0
        problem_words = []

        for word in self.words:
            self.Word.emit(word)
            try:
                # print('Downloading media for word: {}'.format(word.get('wordValue')))
                utils.send_to_download(word, self)
            except (urllib.error.URLError, socket.error):
                problem_words.append(word.get('wordValue'))
            counter += 1
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
