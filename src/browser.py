"""
Browser interaction utilities for the Broadway Lottery Bot.
"""
import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger


class BrowserHandler:
    """Handles browser interactions for the Broadway Lottery Bot."""

    def __init__(self, config):
        """Initialize the browser handler with configuration."""
        self.config = config
        self.driver = None
        self.timeout = config['browser']['timeout']

    def setup_driver(self):
        """Set up and configure the Chrome WebDriver."""
        chrome_options = Options()
        
        if self.config['browser']['headless']:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        if self.config['browser']['user_agent']:
            chrome_options.add_argument(f"--user-agent={self.config['browser']['user_agent']}")
        
        # For Docker environment
        if os.environ.get('RUNNING_IN_DOCKER', False):
            self.driver = webdriver.Chrome(options=chrome_options)
        else:
            # For local development
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        self.driver.set_page_load_timeout(self.timeout)
        logger.info("Browser driver set up successfully")
        return self.driver

    def close(self):
        """Close the browser and clean up resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("Browser closed")

    def navigate_to(self, url):
        """Navigate to the specified URL."""
        try:
            self.driver.get(url)
            logger.info(f"Navigated to {url}")
            return True
        except TimeoutException:
            logger.error(f"Timeout while navigating to {url}")
            return False

    def wait_for_element(self, by, value, timeout=None):
        """Wait for an element to be present and visible."""
        if timeout is None:
            timeout = self.timeout
        
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"Timeout waiting for element {by}={value}")
            return None

    def find_element_safe(self, by, value):
        """Safely find an element, returning None if not found."""
        try:
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            logger.warning(f"Element not found: {by}={value}")
            return None

    def find_elements_safe(self, by, value):
        """Safely find elements, returning empty list if none found."""
        try:
            elements = self.driver.find_elements(by, value)
            return elements
        except NoSuchElementException:
            logger.warning(f"No elements found: {by}={value}")
            return []

    def click_element(self, element, random_delay=True):
        """Click an element with optional random delay to appear more human-like."""
        if random_delay:
            # Random delay between 0.5 and 2 seconds
            time.sleep(random.uniform(0.5, 2))
        
        try:
            element.click()
            return True
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            return False

    def fill_input(self, element, text, random_typing=True):
        """Fill an input field with text, optionally simulating human typing."""
        try:
            element.clear()
            
            if random_typing:
                # Simulate human typing with random delays
                for char in text:
                    element.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.2))
            else:
                element.send_keys(text)
            
            return True
        except Exception as e:
            logger.error(f"Error filling input: {e}")
            return False

    def is_logged_in(self):
        """Check if the user is currently logged in on Rush Telecharge."""
        # Take a screenshot for debugging
        self.take_screenshot("login_check.png")
        
        # First, check if the login form is still visible
        login_form = self.find_element_safe(By.ID, "login_form")
        if login_form and login_form.is_displayed():
            logger.info("Login form is still visible - user is NOT logged in")
            return False
        
        # Check if we're on a page that only logged-in users can access
        current_url = self.driver.current_url.lower()
        logged_in_urls = [
            "account", "profile", "my-", "dashboard", "entries", "lotteries"
        ]
        
        if any(url_part in current_url for url_part in logged_in_urls):
            logger.info(f"Current URL '{current_url}' suggests user is logged in")
            return True
        
        # Check for elements that indicate a NOT logged-in state
        sign_in_indicators = [
            # Check for <a> tags with sign-in text
            (By.XPATH, "//a[contains(text(), 'Sign In')]"),
            (By.XPATH, "//a[contains(text(), 'Log In')]"),
            # Check for <button> tags with sign-in text
            (By.XPATH, "//button[contains(text(), 'Sign In')]"),
            (By.XPATH, "//button[contains(text(), 'Log In')]"),
            # Check for specific button with name attribute
            (By.XPATH, "//button[@name='submit' and contains(text(), 'Sign In')]"),
            # Check for common login-related classes
            (By.CSS_SELECTOR, ".sign-in-button, .login-button, a.login, button.login"),
            # Check for any element with sign-in text
            (By.XPATH, "//*[text()='Sign In' or text()='Log In' or text()='Login']")
        ]
        
        for by, value in sign_in_indicators:
            element = self.find_element_safe(by, value)
            if element and element.is_displayed():
                logger.info(f"Sign in element found: {element.tag_name} - user is NOT logged in")
                return False
        
        # Check for elements that indicate a logged-in state
        logged_in_indicators = [
            # Check for <a> tags with sign-out text
            (By.XPATH, "//a[contains(text(), 'Sign Out')]"),
            (By.XPATH, "//a[contains(text(), 'Log Out')]"),
            # Check for <button> tags with sign-out text
            (By.XPATH, "//button[contains(text(), 'Sign Out')]"),
            (By.XPATH, "//button[contains(text(), 'Log Out')]"),
            # Check for account-related links
            (By.XPATH, "//a[contains(text(), 'My Account')]"),
            (By.XPATH, "//a[contains(text(), 'Account')]"),
            (By.XPATH, "//a[contains(text(), 'Profile')]"),
            (By.XPATH, "//span[contains(text(), 'My Account')]"),
            # Check for common logged-in classes
            (By.CSS_SELECTOR, ".user-profile, .account-menu, .logout-button, .user-menu")
        ]
        
        for by, value in logged_in_indicators:
            element = self.find_element_safe(by, value)
            if element and element.is_displayed():
                logger.info(f"Logged-in indicator found: {element.tag_name} - user is logged in")
                return True
        
        # If we can't definitively determine the login state, check for personalized content
        # This might include a greeting with the user's name or other personalized elements
        personalized_indicators = [
            (By.XPATH, "//div[contains(@class, 'user-greeting')]"),
            (By.XPATH, "//div[contains(@class, 'welcome-message')]"),
            (By.XPATH, "//div[contains(@class, 'account-info')]"),
            # Check for welcome text with email
            (By.XPATH, f"//div[contains(text(), '{self.config['credentials']['username']}')]"),
            (By.XPATH, f"//span[contains(text(), '{self.config['credentials']['username']}')]")
        ]
        
        for by, value in personalized_indicators:
            element = self.find_element_safe(by, value)
            if element and element.is_displayed():
                logger.info("Personalized content found - user is likely logged in")
                return True
        
        # Check if the page has lottery-related content (only visible to logged-in users)
        lottery_indicators = [
            (By.XPATH, "//div[contains(text(), 'Lottery')]"),
            (By.XPATH, "//h1[contains(text(), 'Lottery')]"),
            (By.XPATH, "//h2[contains(text(), 'Lottery')]"),
            (By.XPATH, "//a[contains(text(), 'Enter Lottery')]"),
            (By.CSS_SELECTOR, ".lottery-entry, .lottery-list, .entry-button")
        ]
        
        for by, value in lottery_indicators:
            element = self.find_element_safe(by, value)
            if element and element.is_displayed():
                logger.info("Lottery content found - user is likely logged in")
                return True
        
        # Check if there are any forms that would only be visible to logged-in users
        entry_forms = self.find_elements_safe(By.TAG_NAME, "form")
        for form in entry_forms:
            if form.is_displayed() and "login" not in form.get_attribute("id").lower():
                action = form.get_attribute("action") or ""
                if "entry" in action.lower() or "lottery" in action.lower():
                    logger.info("Entry form found - user is likely logged in")
                    return True
        
        # If we've made it this far and haven't found sign-in buttons, assume we're logged in
        # This is a fallback in case the site's structure doesn't match our expected indicators
        if not any(self.find_element_safe(by, value) for by, value in sign_in_indicators):
            logger.info("No sign-in buttons found - assuming user is logged in")
            return True
            
        logger.info("Login state could not be determined - assuming not logged in")
        return False

    def take_screenshot(self, filename):
        """Take a screenshot for debugging purposes."""
        try:
            os.makedirs("data/screenshots", exist_ok=True)
            filepath = f"data/screenshots/{filename}"
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return False
