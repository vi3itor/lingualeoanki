import os
from .six.moves import http_cookiejar
from .six.moves import urllib
import socket
import json

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
        self.msg = ''

    def get_connection(self):
        try:
            if not self.is_authorized():
                status = self.auth()
                if status['error_msg']:
                    self.msg = status['error_msg']
        except (urllib.error.URLError, socket.error) as e:
            self.msg = "Can't authorize. Check your internet connection."
        except ValueError:
            self.msg = "Error! Possibly, invalid data was received from LinguaLeo"
        except Exception as e:
            # TODO improve exception handling
            self.msg = "There's been an unexpected error. Sorry about that! " + str(e.args)
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
            url = 'https://lingualeo.com/ru/userdict3/getWordSets'
            all_wordsets = self.get_content(url, None)["result"]
            wordsets = []
            for wordset in all_wordsets:
                # Add only non-empty dictionaries
                if wordset['countWords'] != 0:
                    wordsets.append(wordset.copy())
            self.save_cookies()
            if not wordsets:
                self.msg = 'No user dictionaries found'
        except (urllib.error.URLError, socket.error):
            self.msg = "Can't get dictionaries. Check your internet connection."
        except ValueError:
            self.msg = "Error! Possibly, invalid data was received from LinguaLeo"
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
            self.msg = "Can't download words. Check your internet connection."
        except ValueError:
            self.msg = "Error! Possibly, invalid data was received from LinguaLeo"

        if self.msg:
            self.Error.emit(self.msg)
            self.msg = ''
            return None

        return words

    def get_all_words(self):
        """
        The JSON consists of list "userdict3" on each page
        Inside of each userdict there is a list of periods with names
        such as "October 2015". And inside of them lay our words.
        Returns: type == list of dictionaries
        """
        words = []
        page_number = 1
        periods = self.get_page(page_number)
        while len(periods) > 0:
            for period in periods:
                words += period['words']
            page_number += 1
            periods = self.get_page(page_number)
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

    def auth(self):
        url = 'https://api.lingualeo.com/api/login'
        values = {'email': self.email, 'password': self.password}
        content = self.get_content(url, values)
        self.save_cookies()
        return content

    def is_authorized(self):
        url = 'https://api.lingualeo.com/api/isauthorized'
        status = self.get_content(url, None)['is_authorized']
        return status

    def get_page(self, page_number):
        url = 'https://lingualeo.com/ru/userdict/json'
        values = {'filter': 'all', 'page': page_number}
        return self.get_content(url, values)['userdict3']

    def get_page_by_group_id(self, group_id, page_number):
        """
        Get the words of a particular user dictionary (wordset)
        """
        url = 'https://lingualeo.com/ru/userdict/json'
        values = {'filter': 'all', 'page': page_number, 'groupId': group_id}
        return self.get_content(url, values)['userdict3']

    def get_content(self, url, values):
        url_values = urllib.parse.urlencode(values) if values else None
        full_url = url + '?' + url_values if url_values else url
        req = self.opener.open(full_url)
        return json.loads(req.read())

    # TODO: Measure http vs https speed and
    #  consider adding 'http' option to config

    # TODO: Add processing of http status codes and raise an exception,
    #  see: http://docs.python-requests.org/en/master/user/quickstart/#response-status-codes


def is_word_exist(check_word, words):
    """
    Helper function to test if check_word dictionary exists in the list of words
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
