import json
import urllib
import urllib2
from cookielib import CookieJar

class Lingualeo:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.cj = CookieJar()

    def auth(self):
        url = "http://api.lingualeo.com/api/login"
        values = {"email": self.email, "password": self.password}
        return self.get_content(url, values)

    def get_page(self, page_number):
        url = 'http://lingualeo.com/ru/userdict/json'
        values = {'filter': 'all', 'page': page_number}
        return self.get_content(url, values)['userdict3']

    def get_content(self, url, values):
        data = urllib.urlencode(values)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        req = opener.open(url, data)
        return json.loads(req.read())


    def get_all_words(self, missed, last_word):
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
                    if missed == 2:
                        if period['words']:
                            for period_word in period['words']:
                                if period_word['word_value'] == last_word:
                                    return words

                    words += period['words']
            else:
                have_periods = False
            page_number += 1
        return words