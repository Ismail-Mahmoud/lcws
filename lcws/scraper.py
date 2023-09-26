import os
import tomllib
from urllib.parse import urljoin

from click import ClickException
from rich.console import Console
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
with open(f"{CONFIG_DIR}/config.toml", "rb") as f:
    config = tomllib.load(f)


class Scraper:
    DRIVER = {
        "firefox": webdriver.Firefox,
        "chrome": webdriver.Chrome,
    }
    DRIVER_OPTIONS = {
        "firefox": webdriver.FirefoxOptions,
        "chrome": webdriver.ChromeOptions,
    }

    def __init__(
        self, browser: str, headless: bool, timeout: int,
        problem_url: str, submission_url: str, console: Console
    ) -> None:
        driver_options = self.DRIVER_OPTIONS[browser]()
        driver_options.headless = headless
        self.driver: WebDriver = self.DRIVER[browser](options=driver_options)
        self.wait = WebDriverWait(self.driver, timeout)
        self.problem_url = problem_url
        self.submission_url = submission_url
        self.console = console

    def login(self):
        LEETCODE_USER = config["leetcode"]["user"]
        LEETCODE_PASSWORD = config["leetcode"]["password"]
        LEETCODE_LOGIN_PAGE = config["leetcode"]["login_page"]

        if not LEETCODE_USER or not LEETCODE_PASSWORD:
            raise ClickException("Please provide your LeetCode credentials.")

        self.driver.get(LEETCODE_LOGIN_PAGE)
        self.console.log("[dim]Current Page:", self.driver.current_url)

        try:
            user: WebElement = self.wait.until(
                EC.presence_of_element_located((By.ID, "id_login")))
            password: WebElement = self.wait.until(
                EC.presence_of_element_located((By.ID, "id_password")))
            button: WebElement = self.wait.until(
                EC.element_to_be_clickable((By.ID, "signin_btn")))
        except TimeoutException:
            raise ClickException("[TIMEOUT] Login failed.")

        user.send_keys(LEETCODE_USER)
        password.send_keys(LEETCODE_PASSWORD)

        try:
            button.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click()", button)

        try:
            self.wait.until(EC.url_changes(LEETCODE_LOGIN_PAGE))
        except TimeoutException:
            raise ClickException(
                "[TIMEOUT] Login failed. Make sure you provided the correct credentials.")

    def fetch_problem_title(self) -> str:
        self.driver.get(self.problem_url)
        self.console.log("[dim]Current Page:", self.driver.current_url)

        slug = self.problem_url.rstrip("/").split("/")[-1]

        try:
            element: WebElement = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class='flex-1']")))
            title = element.text
        except TimeoutException:
            self.console.log(
                "[yellow]Couldn't extract problem title, using slug instead...")
            title = slug

        return title

    def fetch_solution_details(self) -> tuple[str, str]:
        self.go_to_submission_page()
        try:
            code: str = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "code"))).text
        except TimeoutException:
            raise ClickException("[TIMEOUT] Couldn't extract the solution.")

        try:
            language: str = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class='mb-4']"))).text
        except TimeoutException:
            self.console.log("[yellow]Couldn't detect the solution language.")
            language = ""

        return code, language

    def go_to_submission_page(self):
        if self.submission_url is not None:
            self.driver.get(self.submission_url)
            self.console.log("[dim]Current Page:", self.driver.current_url)
            return

        submissions_url = urljoin(self.problem_url, "submissions")
        self.driver.get(submissions_url)
        self.console.log("[dim]Current Page:", self.driver.current_url)

        try:
            last_accepted_submission: WebElement = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Accepted']")))
            last_accepted_submission.click()
        except ElementClickInterceptedException:
            self.driver.execute_script(
                "arguments[0].click()", last_accepted_submission)
        except:
            raise ClickException(
                "Couldn't detect any accepted submissions, please provide a valid submission URL.")

        try:
            self.wait.until(EC.url_changes(submissions_url))
        except TimeoutException:
            raise ClickException("[TIMEOUT] Couldn't load submission page.")

        self.console.log("[dim]Current Page:", self.driver.current_url)
