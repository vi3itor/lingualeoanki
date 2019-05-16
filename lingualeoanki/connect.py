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
            values = {'request': [{'type': 'user', 'perPage': 999, 'sortBy': 'created'}]}
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

    def get_words_to_add(self, status, wordsets=None):
        if not self.get_connection():
            return None
        try:
            words = self.get_words(status, wordsets)
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

    def get_words(self, status, wordsets):
        """
        TODO: Update description
        """
        url = 'mobile-api.lingualeo.com/GetWords'
        # TODO: Move parameter to config?
        PER_PAGE = 30
        values = {'perPage': PER_PAGE, 'page': 1, 'status': status}
        pages = 0

        if wordsets:
            wordset_ids = []
            # Since words can repeat in the wordsets, we calculate upper bound
            max_words = 0
            for wordset in wordsets:
                wordset_ids.append(wordset['id'])
                max_words += wordset['cw'] if 'cw' in wordset else wordset['countWords']
            values['wordSetIds'] = wordset_ids
            pages = max_words // PER_PAGE + 1

        response = self.get_content_new(url, values)
        words = response['data']

        if not wordsets:
            # Calculate total number of pages since each response contains PER_PAGE words only
            pages = response['wordSet']['countWords'] // PER_PAGE + 1

        # Continue getting the words starting from the second page
        for page in range(2, pages + 1):
            values['page'] = page
            next_chunk = self.get_content_new(url, values)['data']
            if next_chunk:
                words += next_chunk
            else:
                # Empty page, there are no more words
                return words
        return words

    def save_cookies(self):
        if hasattr(self, 'cookies_path'):
            self.cj.save(self.cookies_path)

    def get_token(self):
        if hasattr(self, 'token'):
            return self.token
        for cookie in self.cj:
            if cookie.name == 'remember':
                self.token = cookie.value
                return self.token

    # Low level methods
    #########################

    def get_content_new(self, url, more_values):
        """
        A new API method to request content
        """
        values = {'apiVersion': '1.0.0',
                  'token': self.get_token()}
        values.update(more_values)
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
        self.get_token()
        return content

    def is_authorized(self):
        url = 'api.lingualeo.com/api/isauthorized'
        status = self.get_content(url, None)['is_authorized']
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
                problem_words.append(word.get('wd'))
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
