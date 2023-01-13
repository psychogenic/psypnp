'''

HTML stripper for python2,
pretty much straight from
https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python

'''

from HTMLParser import HTMLParser
from StringIO import StringIO



class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(htmlStr):
    
    if htmlStr is None or not len(htmlStr):
        return '' 
    
    s = MLStripper()
    s.feed(htmlStr)
    return s.get_data()
