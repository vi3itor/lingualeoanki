import requests
import pickle


class Lingualeo:
    def __init__(self, email, password, cookies_path=None):
        self.email = email
        self.password = password
        self.cookies_path = cookies_path
        self.cj = requests.cookies.RequestsCookieJar()
        try:
            with open(cookies_path, 'rb') as f:
                cookies = pickle.load(f)
                self.cj.update(cookies)
        except:
            # TODO: narrow exception clause (FileNotFound, pickle.UnpicklingError, etc)
            self.cj = requests.cookies.RequestsCookieJar()

    def auth(self):
        url = 'https://api.lingualeo.com/api/login'
        values = {'email': self.email, 'password': self.password}
        content = self.get_content(url, values)
        if hasattr(self, 'cookies_path'):
            with open(self.cookies_path, 'wb+') as f:
                pickle.dump(self.cj, f)

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
        r = requests.get(url, params=values, cookies=self.cj)
        self.cj.update(r.cookies)
        return r.json()

    # TODO: Measure http vs https speed and
    #  consider adding 'http' option to config

    # TODO: should we update cookies file with every request?
    #  Or only in auth() and get_wordsets, get_all_words...

    # TODO: Add processing of http status codes and raise an exception,
    #  see: http://docs.python-requests.org/en/master/user/quickstart/#response-status-codes

    def get_wordsets(self):
        """
        Get user's dictionaries (wordsets), including default ones,
        and return those, that are not empty
        """
        url = 'https://lingualeo.com/ru/userdict3/getWordSets'
        all_wordsets = self.get_content(url, None)["result"]
        wordsets = []
        for wordset in all_wordsets:
            # Add only non-empty dictionaries
            if wordset['countWords'] != 0:
                wordsets.append(wordset.copy())
        return wordsets

    def get_words(self, wordsets=None):
        if wordsets:
            return self.get_words_by_wordsets(wordsets)
        else:
            return self.get_all_words()

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


def is_word_exist(check_word, words):
    for word in words:
        if word['word_id'] == check_word['word_id']:
            return True
    return False
