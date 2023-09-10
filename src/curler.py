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
        raise NotImplementedError


class SeleniumCurler(Curler):
    def __init__(
        self,
        page_source_wait: float = 0.25,
    ):
        super().__init__()
        self.page_source_wait = page_source_wait
        self.extra_execs: list[Callable[[WebDriver], None]] = []
        self.index_error_wait_time: float | int = 1
        self.button_tries = 3
        self.backup_button_args: tuple | None = None
        self.pre_wait_time = 0
        self.__selenium_webdriver = None

    @property
    def selenium_webdriver(self):
        if self.__selenium_webdriver is None:
            self.__selenium_webdriver = webdriver.Chrome()
            self.__selenium_webdriver.maximize_window()
            # self.__selenium_webdriver.minimize_window()
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
        # run extra arguments
        for extra_exec in self.extra_execs:
            extra_exec(self.selenium_webdriver)
        # click buttons
        for button in buttons:
            find_element_by, find_element_by_arg, index, wait_time = button
            for _ in range(self.button_tries):
                try:
                    element = self.selenium_webdriver.find_elements(
                        find_element_by, find_element_by_arg
                    )[index]
                    self.selenium_webdriver.execute_script(
                        "arguments[0].scrollIntoView();", element
                    )
                    element.click()
                    break
                except (
                    IndexError,
                    selenium.common.exceptions.ElementNotInteractableException,
                    selenium.common.exceptions.ElementClickInterceptedException,
                    selenium.common.exceptions.StaleElementReferenceException,
                ) as e:
                    raise
                    print(
                        f"Warning: {find_element_by} {find_element_by_arg} {index} got error: {type(e).__name__}. Trying again"
                    )
                    if self.backup_button_args is not None:
                        (
                            backup_find_element_by,
                            backup_find_element_by_arg,
                        ) = self.backup_button_args
                        try:
                            backup_buttons = self.selenium_webdriver.find_elements(
                                backup_find_element_by, backup_find_element_by_arg
                            )
                            for backup_button in backup_buttons:
                                self.selenium_webdriver.execute_script(
                                    "arguments[0].scrollIntoView();", backup_button
                                )
                                backup_button.click()
                        except (
                            selenium.common.exceptions.ElementClickInterceptedException,
                            selenium.common.exceptions.ElementNotInteractableException,
                        ):
                            print("Backup button click intercepted. Trying again")
                            pass
                    time.sleep(self.index_error_wait_time)
                    continue
            else:
                raise
                try:
                    element = self.selenium_webdriver.find_elements(
                        find_element_by, find_element_by_arg
                    )[index]
                    print(f"Final click attempt on element: {element}")
                    element.click()
                except KeyboardInterrupt:
                    raise
                except:
                    raise RuntimeError("Selenium curler failed to click button.")
            time.sleep(wait_time)
        # sleep for a bit to let the page load
        time.sleep(self.page_source_wait)
        return

    def urlget(self, url: str, buttons: tuple[tuple] = tuple()) -> str:
        time.sleep(self.pre_wait_time)
        try:
            self.selenium_webdriver.get(url)
        except selenium.common.exceptions.TimeoutException:
            print("Got timeout exception. Resetting and trying again")
            self.reset_webdriver()
            self.selenium_webdriver.get(url)
        self.prep_for_scrape(buttons)
        page_source = self.selenium_webdriver.page_source
        return page_source
