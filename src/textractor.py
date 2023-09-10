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
