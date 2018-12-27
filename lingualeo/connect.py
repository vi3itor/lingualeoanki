import json
import urllib.request
import urllib.parse
import urllib.error

from http.cookiejar import CookieJar


class Lingualeo:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.cj = CookieJar()

    def auth(self):
        url = "http://api.lingualeo.com/api/login"
        values = {"email": self.email, "password": self.password}
        # TODO: Save and load cookies. Use API call "isauthorized"
        return self.get_content(url, values)

    def get_page(self, page_number):
        url = 'http://lingualeo.com/ru/userdict/json'
        values = {'filter': 'all', 'page': page_number}
        return self.get_content(url, values)['userdict3']

    # Get the words of a particular wordset
    def get_page_by_group_id(self, group_id, page_number):
        url = 'http://lingualeo.com/ru/userdict/json'
        values = {'filter': 'all', 'page': page_number, 'groupId': group_id}
        return self.get_content(url, values)['userdict3']

    def get_content(self, url, values):
        data = urllib.parse.urlencode(values).encode("utf-8") if values else None
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        req = opener.open(url, data)
        return json.loads(req.read())

    def get_all_words(self):  # , missed, last_word):
        """
        The JSON consists of list "userdict3" on each page
        Inside of each userdict there is a list of periods with names
        such as "October 2015". And inside of them lay our words.
        Returns: type == list of dictionaries
        """
        words = []
        have_periods = True
        page_number = 1
        while have_periods:
            periods = self.get_page(page_number)
            if len(periods) > 0:
                for period in periods:
                    # if missed can be 2(True) or 0(False)
                    # i have no idea why True doesn't output
                    # if missed == 2:
                    #     if period['words']:
                    #         for period_word in period['words']:
                    #             if period_word['word_value'] == last_word:
                    #                 return words
                    words += period['words']
            else:
                have_periods = False
            page_number += 1
        return words

    def get_words_by_wordsets(self, wordsets):
        words = []
        # TODO: Consider not adding words that are included in multiple wordsets
        for wordset in wordsets:
            page_number = 1
            group_id = wordset['id']
            periods = self.get_page_by_group_id(group_id, page_number)
            while len(periods) > 0:
                for period in periods:
                    words += period['words']
                page_number += 1
                periods = self.get_page_by_group_id(group_id, page_number)
        return words

    def get_wordsets(self):
        """
        Get user's wordsets, including default ones,
        and return non empty
        """
        url = "https://lingualeo.com/ru/userdict3/getWordSets"
        # get all wordsets (including empty ones)
        all_wordsets = self.get_content(url, None)["result"]
        wordsets = []

        for wordset in all_wordsets:
            if wordset['countWords'] != 0:
                wordsets.append(wordset.copy())

        return wordsets
