import pprint as pp
import re

from bs4 import BeautifulSoup
import requests

from curler import SeleniumCurler


class Textractor:
    """Base class for text extraction from url."""

    def __init__(self):
        self.__curler = None

    @property
    def curler(self):
        if self.__curler is None:
            self.__curler = SeleniumCurler()
        return self.__curler
    
    def urlget(self, url: str):
        """Wrapper around curler urlget."""
        return self.curler.urlget(url)

    def textract(self, page_source: str) -> str:
        """Extract text from the page source.

        Args:
            page_source (str)

        Returns:
            str: The extracted text.
        """
        raise NotImplementedError
    
    def __call__(self, url: str) -> str:
        """Extract text from the url.

        Args:
            url (str)

        Returns:
            str: The extracted text.
        """
        page_source = self.urlget(url)
        return self.textract(page_source)
    

class WikipediaTextractor(Textractor):
    """Textractor for wikipedia"""
    def urlget(self, url: str):
        """Wrapper around requests urlget."""
        return requests.get(url).text
    
    def textract(self, page_source: str) -> str:
        soup = BeautifulSoup(page_source, 'html.parser')
        main_content = soup.select_one('div#mw-content-text > div.mw-parser-output')
        main_content.select_one('div.reflist').extract()
        for table in main_content.select('table'):
            table.extract()
        for img in main_content.select('img'):
            img.extract()
        for figure in main_content.select('figure'):
            figure.extract()
        return main_content.get_text()
    

class StackExchangeTextractor(Textractor):
    """Textractor for stackexchange.com."""

    def textract(self, page_source: str) -> str:
        soup = BeautifulSoup(page_source, 'html.parser')
        text = []
        # get title
        question_header_element = soup.find('div', attrs={'id': 'question-header'})
        question_link_element = question_header_element.find('a', class_='question-hyperlink')
        text.append(question_link_element.get_text())
        # get question/answer bodies
        for post in soup.find_all('div', class_='js-post-body'):
            text.append(re.sub(r'\n+', '\n', post.get_text().strip()))
        return '\n\n'.join(text)
    

if __name__ == '__main__':
    # test stackexchange extraction
    textractor = StackExchangeTextractor()
    url = 'https://stackoverflow.com/questions/31324218/scikit-learn-how-to-obtain-true-positive-true-negative-false-positive-and-fal'
    text = textractor(url)
    print(text)
    # test wikipedia extraction
    textractor = WikipediaTextractor()
    url = 'https://en.wikipedia.org/wiki/Louis_XIV'
    text = textractor(url)
    print(text)
