import pprint as pp
import re

from bs4 import BeautifulSoup

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
    

class StackExchangeTextractor(Textractor):
    """Textractor for stackexchange.com."""

    def textract(self, page_source: str) -> str:
        soup = BeautifulSoup(page_source, 'html.parser')
        text = []
        # get title
        question_header_element = soup.find('div', attrs={'id': 'question-header'})
        text.append(question_header_element.get_text())
        # get question/answer bodies
        for post in soup.find_all('div', class_='js-post-body'):
            text.append(re.sub(r'\n+', '\n', post.get_text().strip()))
        return '\n\n'.join(text)
    

if __name__ == '__main__':
    # test extraction
    textractor = StackExchangeTextractor()
    url = 'https://stackoverflow.com/questions/31324218/scikit-learn-how-to-obtain-true-positive-true-negative-false-positive-and-fal'
    text = textractor(url)
    print(text)
