import time
from typing import Callable
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
import selenium.common.exceptions
from selenium.webdriver.common.by import By


class Curler:
    def __init__(self):
        pass

    def urlget(self, url: str) -> str:
        """Get the page source of the given url.
        
        Args:
            url (str)
            
        Returns:
            str: page source"""
        raise NotImplementedError


class SeleniumCurler(Curler):
    def __init__(
        self,
        page_source_wait: float = 0.25,
    ):
        super().__init__()
        self.page_source_wait = page_source_wait
        self.__selenium_webdriver = None

    @property
    def selenium_webdriver(self):
        if self.__selenium_webdriver is None:
            options = webdriver.FirefoxOptions()
            options.headless = True
            self.__selenium_webdriver = webdriver.Firefox(options=options)
            self.__selenium_webdriver.maximize_window()
        return self.__selenium_webdriver
    
    def delete_webdriver(self):
        """
        Close webdriver and set to none
        """
        if self.__selenium_webdriver is not None:
            self.__selenium_webdriver.close()
        self.__selenium_webdriver = None
    
    def reset_webdriver(self):
        """
        Close webdriver, set to none, and reopen to https://en.wikipedia.org/
        """
        if self.__selenium_webdriver is not None:
            self.__selenium_webdriver.close()
        self.__selenium_webdriver = None
        self.selenium_webdriver.get("https://en.wikipedia.org/")

    def prep_for_scrape(self, buttons: tuple[tuple] = tuple()):
        """Prepare the selenium webdriver for scraping. Assumes the webdriver is already on the page."""
        # sleep for a bit to let the page load
        time.sleep(self.page_source_wait)
        # scroll to the bottom of the page
        self.selenium_webdriver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        # sleep for a bit to let the page load
        time.sleep(self.page_source_wait)
        return

    def urlget(self, url: str, buttons: tuple[tuple] = tuple()) -> str:
        try:
            self.selenium_webdriver.get(url)
        except selenium.common.exceptions.TimeoutException:
            print("Got timeout exception. Resetting and trying again")
            self.reset_webdriver()
            self.selenium_webdriver.get(url)
        self.prep_for_scrape(buttons)
        page_source = self.selenium_webdriver.page_source
        return page_source
