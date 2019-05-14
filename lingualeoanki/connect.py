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
        config = utils.get_config()
        self.url_prefix = config['protocol'] if config else 'https://'
        self.msg = ''
        self.tried_ssl_fix = False
        # TODO: Temporary fix until know how to request words from a particular wordset
        self.words = []

    def get_connection(self):
        try:
            if not self.is_authorized():
                status = self.auth()
                if status['error_msg']:
                    self.msg = status['error_msg']
        except (urllib.error.URLError, socket.error) as e:
            # TODO: Find better (secure) fix
            """
            SSLError was noticed on MacOS, because Python 3.6m used in Anki doesn't have 
            security certificates downloaded. The easiest (but unsecure) way is to create SSL context.
            """
            if 'SSL' in str(e.args) and not self.tried_ssl_fix:
                # Problem with https connection, trying ssl fix
                # TODO: check if necessary to clean cookies and create empty
                # utils.clean_cookies()
                # self.cj = http_cookiejar.MozillaCookieJar()

                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                https_handler = urllib.request.HTTPSHandler(context=context)
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
            url = 'mobile-api.lingualeo.com/GetWordSets'
            # TODO: Should we download 'not user' dictionaries too?
            values = {'apiVersion': '1.0.0',
                      'request': [{'type': 'user', 'perPage': 500}],
                      'token': self.token}
            all_wordsets = self.get_content_new(url, values)['data'][0]['items']
            wordsets = []
            # Add only non-empty dictionaries
            for wordset in all_wordsets:
                """
                Apparently, first dictionary has attribute 'countWords', 
                while others has attribute 'cw'
                """
                if 'cw' in wordset and wordset['cw'] != 0:
                    wordsets.append(wordset.copy())
                elif 'countWords' in wordset and wordset['countWords'] != 0:
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

    def get_words_to_add(self, wordsets=None):
        if not self.get_connection():
            return None
        try:
            words = self.get_words_by_wordsets(wordsets) if wordsets else self.get_all_words()
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

    def get_all_words(self):
        """
        TODO: Update description
        """

        url = 'mobile-api.lingualeo.com/GetWords'
        values = {'apiVersion': '1.0.0',
                  'page': 1,
                  # 'request': [{}],  # 'perPage': 500
                  'token': self.token}

        words = []
        response = self.get_content_new(url, values)
        words += response['data']
        pages = 0
        # Calculate total number of pages since each response contains 20 words only
        if 'wordSet' in response:
            pages = response['wordSet']['countWords'] // 20 + 1

        if pages < 2:  # Only one page or something is wrong
            return words

        # Continue getting the words from the second page
        for page in range(2, pages + 1):
            values['page'] = page
            words += self.get_content_new(url, values)['data']
        return words

    def get_words_by_wordsets(self, wordsets):
        """
        Since each word can belong to multiple dictionaries (wordsets),
        we return a list of unique words only.
        """
        unique_words = []
        for wordset in wordsets:
            page_number = 1
            group_id = wordset['id']
            periods = self.get_page_by_group_id(group_id, page_number)
            while len(periods) > 0:
                for period in periods:
                    words = period['words']
                    for word in words:
                        if not is_word_exist(word, unique_words):
                            unique_words.append(word)
                page_number += 1
                periods = self.get_page_by_group_id(group_id, page_number)
        return unique_words

    def save_cookies(self):
        if hasattr(self, 'cookies_path'):
            self.cj.save(self.cookies_path)

    # Low level methods
    #########################

    def get_token(self):
        for cookie in self.cj:
            if cookie.name == 'remember':
                return cookie.value

    def get_content_new(self, url, values):
        """
        A new API method to request content
        """
        token = self.get_token()
        full_url = self.url_prefix + url
        json_data = json.dumps(values)
        data = json_data.encode('utf-8')
        req = urllib.request.Request(full_url)
        req.add_header('Content-Type', 'text/plain')
        response = urllib.request.urlopen(req, data=data)
        return json.loads(response.read())

    """
    Using requests module (only Anki 2.1) it can be performed as:

    def requests_get_content(self, url, data):
        full_url = self.url_prefix + url
        headers = {'Content-Type': 'text/plain'}
        r = requests.post(full_url, json=data, headers=headers)
        # print(r.status_code)
        return r.json()
    """

    """
    OLD API Methods. Some are still used for authorization
    """

    def auth(self):
        url = 'api.lingualeo.com/api/login'
        values = {'email': self.email, 'password': self.password}
        content = self.get_content(url, values)
        self.save_cookies()
        self.token = self.get_token()
        return content

    def is_authorized(self):
        url = 'api.lingualeo.com/api/isauthorized'
        status = self.get_content(url, None)['is_authorized']
        # TODO: Find better place for getting token
        if not hasattr(self, 'token'):
            self.token = self.get_token()
        return status

    def get_page(self, page_number):
        url = 'lingualeo.com/ru/userdict/json'
        values = {'filter': 'all', 'page': page_number}
        return self.get_content(url, values)['userdict3']

    def get_page_by_group_id(self, group_id, page_number):
        """
        Get the words of a particular user dictionary (wordset)
        """
        url = 'lingualeo.com/ru/userdict/json'
        values = {'filter': 'all', 'page': page_number, 'groupId': group_id}
        return self.get_content(url, values)['userdict3']

    def get_content(self, url, values):
        if values:
            url_values = urllib.parse.urlencode(values)
            data = url_values.encode('utf-8')
        else:
            data = None
        full_url = self.url_prefix + url  # + '?' + url_values if url_values else self.url_prefix + url
        req = self.opener.open(full_url, data=data)
        return json.loads(req.read())

    # TODO: Add processing of http status codes in exceptions,
    #  see: http://docs.python-requests.org/en/master/user/quickstart/#response-status-codes


def is_word_exist(check_word, words):
    """
    Helper function to test if a check_word appear in the list of words
    :param check_word: dict
    :param words: list
    :return: bool
    """
    for word in words:
        if word['word_id'] == check_word['word_id']:
            return True
    return False


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
                utils.send_to_download(word, self)
            except (urllib.error.URLError, socket.error):
                problem_words.append(word.get('word_value'))
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
