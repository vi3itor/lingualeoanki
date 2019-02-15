import json
import urllib.request
import urllib.parse
import urllib.error

from http.cookiejar import CookieJar

# TODO: Measure http vs https speed and consider doing https-only requests,
#  or ask user what protocol to use (or use config for that purpose)

class Lingualeo:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.cj = CookieJar()

    def auth(self):
        url = "http://api.lingualeo.com/api/login"
        values = {"email": self.email, "password": self.password}
        # TODO: Save and load cookies to user_files folder. Use is_authorized
        return self.get_content(url, values)

    def is_authorized(self):
        url = 'http://api.lingualeo.com/api/isauthorized'
        status = self.get_content(url, None)
        return status['is_authorized']

    def get_page(self, page_number):
        url = 'http://lingualeo.com/ru/userdict/json'
        values = {'filter': 'all', 'page': page_number}
        return self.get_content(url, values)['userdict3']

    # Get the words of a particular dictionary (wordset)
    def get_page_by_group_id(self, group_id, page_number):
        url = 'http://lingualeo.com/ru/userdict/json'
        values = {'filter': 'all', 'page': page_number, 'groupId': group_id}
        return self.get_content(url, values)['userdict3']

    def get_content(self, url, values):
        data = urllib.parse.urlencode(values).encode("utf-8") if values else None
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        req = opener.open(url, data)
        return json.loads(req.read())

    def get_wordsets(self):
        """
        Get user's dictionaries (wordsets), including default ones,
        and return those, that are not empty
        """
        url = "http://lingualeo.com/ru/userdict3/getWordSets"
        # get all (including empty ones)
        all_wordsets = self.get_content(url, None)["result"]
        wordsets = []
        for wordset in all_wordsets:
            if wordset['countWords'] != 0:
                wordsets.append(wordset.copy())
        return wordsets

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
        unique_words = []
        for wordset in wordsets:
            page_number = 1
            group_id = wordset['id']
            periods = self.get_page_by_group_id(group_id, page_number)
            while len(periods) > 0:
                for period in periods:
                    words = period['words']
                    for word in words:
                        if not self.is_word_exist(word, unique_words):
                            unique_words.append(word)
                page_number += 1
                periods = self.get_page_by_group_id(group_id, page_number)
        return unique_words

    def is_word_exist(self, check_word, words):
        for word in words:
            if word['word_id'] == check_word['word_id']:
                return True
        return False
