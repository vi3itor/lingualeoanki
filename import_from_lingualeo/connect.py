import urllib
import urllib2
import json
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

    def get_words(self):
        ''' 
        Downloads the whole LinguaLeo dictionary 
        Returns: type == list of dictionaries         
        '''        
        url = 'http://api.lingualeo.com/api/userdict'
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        req = opener.open(url)
        return json.loads(req.read())['words']    

    def get_content(self, url, values):
        data = urllib.urlencode(values)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        req = opener.open(url, data)
        return json.loads(req.read())
