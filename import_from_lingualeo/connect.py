import urllib
import urllib2
import json
from cookielib import CookieJar


class Lingualeo:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.cj = CookieJar()
        self.json_url = 'http://lingualeo.com/userdict/json?&filter=all&page='
        self.userdict = []
        self.auth()             

    def auth(self):
        url = "http://api.lingualeo.com/api/login"
        values = {"email": self.email, "password": self.password}
        return self.get_content(url, values)

    def get_page(self, url):
        ''' 
        Downloads words from one page 
        Returns: type == list of dictionaries         
        '''                
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        req = opener.open(url)
        return json.loads(req.read())['userdict3']    

    def get_content(self, url, values):
        data = urllib.urlencode(values)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        req = opener.open(url, data)
        return json.loads(req.read())  

    def get_all_words(self):
        '''
        The JSON consists of list "userdict3" on each page
        Inside an each userdict there is a list of periods with names
        like "October 2015" and so on. And inside of them lay our words.
        '''
        still = True
        n = 1
        while still:
            url = self.json_url + str(n)
            periods = self.get_page(url)
            if len(periods) > 0:
                for period in periods:
                    self.userdict += period['words']                    
            else:
                still = False
            n += 1
            