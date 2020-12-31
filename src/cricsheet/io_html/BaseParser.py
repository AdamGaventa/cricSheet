import urllib
from bs4 import BeautifulSoup
import logging

log = logging.getLogger(__name__)

class BaseParser:

    def __init__(self, url=None):
        self.url = url
        self.soup = None

    def __str__(self):
        return f'Parser Class for url: {self.url}'

    def read_html(self):
        # read url as html

        # using self.url here rather than in function parameter,
        # as never want to read a different url than self.url
        with urllib.request.urlopen(self.url) as url:
            try:
                s = url.read()
                log.debug(f'URL read successfully: {self.url}')
            except:
                pass
        return s

    def create_soup(self, html):
        # create a bs4 soup from the html

        soup = BeautifulSoup(html, 'html.parser')

        return soup

    def execute(self):
        log.debug('Reading url')
        html_page = self.read_html()

        log.debug('Creating a beautiful soup')
        self.soup = self.create_soup(html_page)
