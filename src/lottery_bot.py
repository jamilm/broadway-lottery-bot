"""
Broadway Lottery Bot - Main implementation for automating lottery entries.
"""
import time
import random
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from loguru import logger


class LotteryBot:
    """Bot for automating Broadway lottery entries on Telecharge."""

    def __init__(self, browser_handler, config):
        """Initialize the lottery bot with browser handler and configuration."""
        self.browser = browser_handler
        self.config = config
        self.base_url = config['urls']['base']
        self.login_url = config['urls']['login']
        self.lotteries_url = config['urls']['lotteries']
        
        # Get credentials from environment variables or config
        self.username = self.config['credentials']['username']
        self.password = self.config['credentials']['password']

    def login(self):
        """Log in to the Telecharge website using the modal login form."""
        logger.info("Attempting to log in...")
        
        # Navigate to main page
        if not self.browser.navigate_to(self.login_url):
            logger.error("Failed to navigate to main page")
            return False
        
        # Wait for the page to load
        time.sleep(3)
        
        # Take a screenshot of the initial page
        self.browser.take_screenshot("initial_page.png")
        
        # Log the page source to help with debugging
        logger.info("Analyzing page structure...")
        try:
            page_html = self.browser.driver.page_source
            # Log just a snippet of the HTML to avoid overwhelming the logs
            logger.info(f"Page HTML snippet: {page_html[:500]}...")
            
            # Look for sign-in related elements in the HTML
            if "st_sign_in" in page_html:
                logger.info("Found 'st_sign_in' ID in page source")
            if "st_campaign_login" in page_html:
                logger.info("Found 'st_campaign_login' function reference in page source")
            if "st_style_main_text" in page_html:
                logger.info("Found 'st_style_main_text' class in page source")
            if "st-window" in page_html:
                logger.info("Found 'st-window' iframe in page source")
        except Exception as e:
            logger.error(f"Error analyzing page source: {e}")
        
        # Switch to the iframe first
        logger.info("Attempting to switch to iframe...")
        iframe_found = False
        try:
            # Find the iframe
            iframe = self.browser.find_element_safe(By.ID, "st-window")
            if iframe:
                logger.info("Found iframe with ID 'st-window'")
                # Switch to the iframe
                self.browser.driver.switch_to.frame(iframe)
                logger.info("Successfully switched to iframe")
                iframe_found = True
                self.browser.take_screenshot("after_iframe_switch.png")
            else:
                logger.warning("Could not find iframe with ID 'st-window'")
                # Try to find by other attributes
                iframe = self.browser.find_element_safe(By.XPATH, "//iframe[contains(@src, 'socialtoaster')]")
                if iframe:
                    logger.info("Found iframe by src attribute")
                    self.browser.driver.switch_to.frame(iframe)
                    logger.info("Successfully switched to iframe")
                    iframe_found = True
                    self.browser.take_screenshot("after_iframe_switch.png")
        except Exception as e:
            logger.error(f"Error switching to iframe: {e}")
        
        if not iframe_found:
            logger.warning("Could not find or switch to iframe, continuing with main page...")
        
        # Try multiple approaches to find and click the sign-in button
        sign_in_button = None
        
        # Approach 0: Try to find using the full XPath provided by the user
        logger.info("Approach 0: Using full XPath provided by the user...")
        sign_in_button = self.browser.find_element_safe(By.XPATH, "/html/body/div[1]/div[1]/header/div[2]/div[1]/div/div/a")
        if sign_in_button:
            logger.info("Found sign-in button using full XPath")
            self.browser.take_screenshot("found_signin_button_by_full_xpath.png")
        
        # Approach 1: Try to find by ID
        if not sign_in_button:
            logger.info("Approach 1: Looking for sign-in button by ID...")
            sign_in_button = self.browser.find_element_safe(By.ID, "st_sign_in")
            if sign_in_button:
                logger.info("Found sign-in button by ID 'st_sign_in'")
                self.browser.take_screenshot("found_signin_button_by_id.png")
        
        # Approach 2: Try to find by XPath with onclick attribute
        if not sign_in_button:
            logger.info("Approach 2: Looking for sign-in button by onclick attribute...")
            sign_in_button = self.browser.find_element_safe(
                By.XPATH, 
                "//a[@onclick=\"st_campaign_login();\"] | //a[contains(@onclick, 'st_campaign_login')]"
            )
            if sign_in_button:
                logger.info("Found sign-in button by onclick attribute")
                self.browser.take_screenshot("found_signin_button_by_onclick.png")
        
        # Approach 3: Try to find by class and text
        if not sign_in_button:
            logger.info("Approach 3: Looking for sign-in button by class and text...")
            sign_in_button = self.browser.find_element_safe(
                By.XPATH, 
                "//a[@class='st_style_main_text' and contains(text(), 'Sign In')] | //a[contains(@class, 'st_style_main_text') and contains(text(), 'Sign In')]"
            )
            if sign_in_button:
                logger.info("Found sign-in button by class and text")
                self.browser.take_screenshot("found_signin_button_by_class_and_text.png")
        
        # Approach 4: Try to find any element with 'Sign In' text
        if not sign_in_button:
            logger.info("Approach 4: Looking for any element with 'Sign In' text...")
            sign_in_button = self.browser.find_element_safe(
                By.XPATH, 
                "//*[contains(text(), 'Sign In') or contains(text(), 'Log In') or contains(text(), 'Login')]"
            )
            if sign_in_button:
                logger.info("Found element with sign-in text")
                self.browser.take_screenshot("found_element_with_signin_text.png")
        
        # Approach 5: Use JavaScript to inspect and find potential sign-in elements
        if not sign_in_button:
            logger.info("Approach 5: Using JavaScript to find sign-in elements...")
            try:
                # This JavaScript will log information about potential sign-in elements
                self.browser.driver.execute_script("""
                    console.log('Inspecting page for sign-in elements...');
                    
                    // Log all links on the page
                    var links = document.querySelectorAll('a');
                    console.log('Found ' + links.length + ' links on the page');
                    
                    // Log the first 10 links for debugging
                    for (var i = 0; i < Math.min(links.length, 10); i++) {
                        console.log('Link ' + i + ':', links[i].outerHTML);
                    }
                    
                    // Log all buttons
                    var buttons = document.querySelectorAll('button');
                    console.log('Found ' + buttons.length + ' buttons on the page');
                    
                    // Log the first 10 buttons for debugging
                    for (var i = 0; i < Math.min(buttons.length, 10); i++) {
                        console.log('Button ' + i + ':', buttons[i].outerHTML);
                    }
                    
                    // Look for elements with st_campaign_login in their attributes
                    var elementsWithLogin = [];
                    var allElements = document.querySelectorAll('*');
                    for (var i = 0; i < allElements.length; i++) {
                        var el = allElements[i];
                        if (el.outerHTML.includes('st_campaign_login')) {
                            elementsWithLogin.push(el);
                        }
                    }
                    console.log('Found ' + elementsWithLogin.length + ' elements with st_campaign_login reference');
                    
                    // Log these elements
                    for (var i = 0; i < Math.min(elementsWithLogin.length, 5); i++) {
                        console.log('Element with login reference ' + i + ':', elementsWithLogin[i].outerHTML);
                    }
                """)
                
                # Take a screenshot after JavaScript inspection
                self.browser.take_screenshot("after_js_inspection.png")
                
                # Try to find and click any sign-in element using JavaScript
                clicked = self.browser.driver.execute_script("""
                    // Try to find the exact button first
                    var button = document.getElementById('st_sign_in');
                    if (button) {
                        console.log('Found button by ID:', button);
                        button.click();
                        return true;
                    }
                    
                    // Try to find by onclick attribute
                    var buttons = document.querySelectorAll('a[onclick*=\"st_campaign_login\"]');
                    if (buttons.length > 0) {
                        console.log('Found button by onclick:', buttons[0]);
                        buttons[0].click();
                        return true;
                    }
                    
                    // Try to find by class and text
                    var links = document.querySelectorAll('a.st_style_main_text, a[class*=\"st_style\"]');
                    for (var i = 0; i < links.length; i++) {
                        var text = links[i].textContent.trim().toLowerCase();
                        if (text.includes('sign in') || text.includes('log in') || text.includes('login')) {
                            console.log('Found button by class and text:', links[i]);
                            links[i].click();
                            return true;
                        }
                    }
                    
                    // Try to find any element with sign-in text
                    var allElements = document.querySelectorAll('a, button, div, span');
                    for (var i = 0; i < allElements.length; i++) {
                        var text = allElements[i].textContent.trim().toLowerCase();
                        if (text === 'sign in' || text === 'log in' || text === 'login') {
                            console.log('Found element with exact sign-in text:', allElements[i]);
                            allElements[i].click();
                            return true;
                        }
                    }
                    
                    // If all else fails, try to call the function directly
                    if (typeof st_campaign_login === 'function') {
                        console.log('Calling st_campaign_login() directly');
                        st_campaign_login();
                        return true;
                    }
                    
                    // Last resort: Try to find the login form directly
                    var loginForm = document.getElementById('login_form');
                    if (loginForm) {
                        console.log('Found login form directly:', loginForm);
                        loginForm.style.display = 'block';
                        return true;
                    }
                    
                    return false;
                """)
                
                if clicked:
                    logger.info("Successfully clicked or revealed sign-in element using JavaScript")
                    sign_in_button = True  # Just to indicate we've handled it
                else:
                    logger.warning("Could not find or click sign-in button with JavaScript")
            except Exception as e:
                logger.error(f"Error using JavaScript to find sign-in button: {e}")
        
        # If we still couldn't find the sign-in button, try one last approach
        if not sign_in_button:
            logger.warning("All standard approaches failed. Trying last resort method...")
            try:
                # Try to directly modify the page to show the login form
                login_form_revealed = self.browser.driver.execute_script("""
                    // Try to create a login form if it doesn't exist
                    if (!document.getElementById('login_form')) {
                        console.log('Creating login form...');
                        var form = document.createElement('div');
                        form.id = 'login_form';
                        form.innerHTML = `
                            <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); 
                                        background: white; padding: 20px; z-index: 9999; border: 1px solid #ccc;">
                                <h2>Login</h2>
                                <form>
                                    <div>
                                        <label for="login_email">Email:</label>
                                        <input type="text" id="login_email" name="email">
                                    </div>
                                    <div>
                                        <label for="password">Password:</label>
                                        <input type="password" id="password" name="password">
                                    </div>
                                    <div>
                                        <button type="button" id="get-started-button">Login</button>
                                    </div>
                                </form>
                            </div>
                        `;
                        document.body.appendChild(form);
                        return true;
                    }
                    return false;
                """)
                
                if login_form_revealed:
                    logger.info("Created login form directly in the page")
                    self.browser.take_screenshot("created_login_form.png")
                    sign_in_button = True  # Just to indicate we've handled it
            except Exception as e:
                logger.error(f"Error with last resort method: {e}")
        
        if not sign_in_button:
            logger.error("Could not find sign-in button by any method")
            self.browser.take_screenshot("signin_button_not_found.png")
            return False
        
        # If we found the button with Selenium and it's not just a flag, click it
        if sign_in_button is not True:
            logger.info("Clicking sign-in button...")
            self.browser.click_element(sign_in_button)
        
        # Wait for the login modal to appear
        time.sleep(3)
        
        # Take a screenshot after clicking sign in
        self.browser.take_screenshot("after_signin_click.png")
        
        # Look for the login modal div
        logger.info("Looking for login modal div...")
        login_modal = self.browser.find_element_safe(By.ID, "login_form")
        if not login_modal:
            login_modal = self.browser.find_element_safe(By.CSS_SELECTOR, ".login-modal, .modal, .st_campaign_login_form")
        
        if login_modal:
            logger.info(f"Found login modal: {login_modal.get_attribute('outerHTML')[:100]}...")
            self.browser.take_screenshot("found_login_modal.png")
        else:
            logger.warning("Could not find a specific login modal div, continuing with page-level search")
        
        # Take a screenshot of the login form before finding elements
        self.browser.take_screenshot("login_form_before_finding_elements.png")
        
        # Wait for login form to load in the modal - using the exact IDs provided by the user
        username_field = self.browser.wait_for_element(By.ID, "login_email")
        if username_field:
            logger.info("Found username field by ID 'login_email'")
            self.browser.take_screenshot("found_username_field_by_id.png")
        
        if not username_field:
            username_field = self.browser.wait_for_element(By.NAME, "email")
            if username_field:
                logger.info("Found username field by NAME 'email'")
                self.browser.take_screenshot("found_username_field_by_name.png")
        
        if not username_field:
            username_field = self.browser.find_element_safe(By.CSS_SELECTOR, ".st_campaign_textbox[type='text'], input[type='text'], input[type='email']")
            if username_field:
                logger.info("Found username field by CSS selector")
                self.browser.take_screenshot("found_username_field_by_css.png")
            
        password_field = self.browser.wait_for_element(By.ID, "password")
        if password_field:
            logger.info("Found password field by ID 'password'")
            self.browser.take_screenshot("found_password_field_by_id.png")
        
        if not password_field:
            password_field = self.browser.wait_for_element(By.NAME, "password")
            if password_field:
                logger.info("Found password field by NAME 'password'")
                self.browser.take_screenshot("found_password_field_by_name.png")
        
        if not password_field:
            password_field = self.browser.find_element_safe(By.CSS_SELECTOR, ".st_campaign_textbox[type='password'], input[type='password']")
            if password_field:
                logger.info("Found password field by CSS selector")
                self.browser.take_screenshot("found_password_field_by_css.png")
        
        if not username_field or not password_field:
            logger.error("Login form not found in modal")
            self.browser.take_screenshot("login_form_not_found.png")
            return False
        
        # Take a screenshot before filling in credentials
        self.browser.take_screenshot("before_filling_credentials.png")
        
        # Fill in login credentials
        logger.info(f"Filling username field with: {self.username}")
        self.browser.fill_input(username_field, self.username)
        self.browser.take_screenshot("after_filling_username.png")
        
        logger.info("Filling password field")
        self.browser.fill_input(password_field, self.password)
        self.browser.take_screenshot("after_filling_password.png")
        
        # Find and click the login button in the modal - using the exact ID provided by the user
        login_button = self.browser.find_element_safe(By.ID, "get-started-button")
        if login_button:
            logger.info("Found login button by ID 'get-started-button'")
            self.browser.take_screenshot("found_login_button_by_id.png")
        
        if not login_button:
            login_button = self.browser.find_element_safe(
                By.CSS_SELECTOR, 
                ".st_campaign_button.st_style_button.button_inline"
            )
            if login_button:
                logger.info("Found login button by CSS selector")
                self.browser.take_screenshot("found_login_button_by_css.png")
        
        if not login_button:
            login_button = self.browser.find_element_safe(
                By.XPATH, 
                "//div[contains(text(), 'Login')]"
            )
            if login_button:
                logger.info("Found login button by text content")
                self.browser.take_screenshot("found_login_button_by_text.png")
        
        if not login_button:
            login_button = self.browser.find_element_safe(
                By.XPATH, 
                "//div[@onclick=\"$(this).parents('#login_form').submit();\"]"
            )
            if login_button:
                logger.info("Found login button by onclick attribute")
                self.browser.take_screenshot("found_login_button_by_onclick.png")
        
        if not login_button:
            # Fall back to the original selectors
            login_button = self.browser.find_element_safe(
                By.CSS_SELECTOR, 
                "button[type='submit'], input[type='submit'], .login-submit, .btn-login"
            )
            if login_button:
                logger.info("Found login button by general submit selectors")
                self.browser.take_screenshot("found_login_button_by_general_selectors.png")
            
            if not login_button:
                login_button = self.browser.find_element_safe(
                    By.XPATH, 
                    "//button[contains(text(), 'Log In') or contains(text(), 'Sign In') or contains(text(), 'Login')]"
                )
                if login_button:
                    logger.info("Found login button by general text content")
                    self.browser.take_screenshot("found_login_button_by_general_text.png")
        
        if not login_button:
            logger.error("Login button not found in modal")
            self.browser.take_screenshot("login_button_not_found.png")
            
            # Try to submit the form directly as a last resort
            try:
                logger.warning("Attempting to submit the login form directly...")
                self.browser.take_screenshot("before_form_submit_js.png")
                self.browser.driver.execute_script("""
                    var form = document.getElementById('login_form');
                    if (form) {
                        if (typeof form.submit === 'function') {
                            form.submit();
                        } else {
                            // If it's not a form element, try to find a form inside it
                            var innerForm = form.querySelector('form');
                            if (innerForm) {
                                innerForm.submit();
                            }
                        }
                    }
                """)
                logger.info("Executed form submit via JavaScript")
                time.sleep(5)  # Wait for the login process
                self.browser.take_screenshot("after_form_submit_js.png")
            except Exception as e:
                logger.error(f"Failed to submit form via JavaScript: {e}")
                return False
        else:
            # Click the login button
            logger.info(f"Found login button: {login_button.get_attribute('outerHTML')}")
            self.browser.take_screenshot("before_clicking_login_button.png")
            self.browser.click_element(login_button)
            logger.info("Clicked login button")
            
            # Wait for login to complete
            time.sleep(5)  # Give some time for the login process
        
        # Take a screenshot after login attempt
        self.browser.take_screenshot("after_login_attempt.png")
        
        # Switch back to default content before checking login status
        try:
            self.browser.driver.switch_to.default_content()
            logger.info("Switched back to default content")
        except Exception as e:
            logger.error(f"Error switching back to default content: {e}")
        
        # Check if login was successful
        if self.browser.is_logged_in():
            logger.info("Login successful")
            return True
        else:
            logger.error("Login failed")
            self.browser.take_screenshot("login_failed.png")
            return False

    def navigate_to_lotteries(self):
        """Navigate to the SocialToaster lottery selection page."""
        logger.info("Navigating to lottery selection page...")
        
        # First, we need to find and click the "Enter the Lottery" button on the main page
        # after logging in, before we can navigate to the SocialToaster page
        enter_lottery_button = self.browser.find_element_safe(
            By.XPATH, 
            "//a[contains(text(), 'Enter the Lottery') or contains(text(), 'Enter Lottery')]"
        )
        
        if not enter_lottery_button:
            # Try alternative selectors
            enter_lottery_button = self.browser.find_element_safe(
                By.CSS_SELECTOR, 
                ".lottery-button, .enter-lottery, a.lottery"
            )
        
        if enter_lottery_button:
            logger.info("Found 'Enter the Lottery' button on main page, clicking it...")
            self.browser.click_element(enter_lottery_button)
            time.sleep(3)  # Wait for navigation to complete
            
            # Take a screenshot to see where we are
            self.browser.take_screenshot("after_enter_lottery_click.png")
            
            # Check if we need to navigate directly to the lotteries URL
            current_url = self.browser.driver.current_url
            if "socialtoaster.com" not in current_url:
                logger.info("Not on SocialToaster page yet, navigating directly...")
                return self.browser.navigate_to(self.lotteries_url)
            
            return True
        else:
            # If we can't find the button, try navigating directly to the lotteries URL
            logger.warning("Could not find 'Enter the Lottery' button, navigating directly to lottery URL...")
            return self.browser.navigate_to(self.lotteries_url)

    def get_available_lotteries(self):
        """Get a list of all available lotteries from the SocialToaster page."""
        logger.info("Finding available lotteries on SocialToaster page...")
        
        # Wait for the lotteries page to load
        time.sleep(5)
        
        # Take a screenshot of the lottery page for debugging
        self.browser.take_screenshot("lottery_selection_page.png")
        
        # Make sure we're in the iframe that contains the lottery content
        try:
            # First, switch back to default content to ensure we're starting from the main page
            self.browser.driver.switch_to.default_content()
            logger.info("Switched to default content")
            
            # Find the iframe with ID "st-window"
            iframe = self.browser.find_element_safe(By.ID, "st-window")
            if iframe:
                logger.info("Found iframe with ID 'st-window'")
                # Switch to the iframe
                self.browser.driver.switch_to.frame(iframe)
                logger.info("Successfully switched to iframe")
                self.browser.take_screenshot("inside_lottery_iframe.png")
            else:
                # Try to find by other attributes
                iframe = self.browser.find_element_safe(By.XPATH, "//iframe[contains(@src, 'socialtoaster')]")
                if iframe:
                    logger.info("Found iframe by src attribute")
                    self.browser.driver.switch_to.frame(iframe)
                    logger.info("Successfully switched to iframe")
                    self.browser.take_screenshot("inside_lottery_iframe.png")
                else:
                    logger.warning("Could not find the SocialToaster iframe")
        except Exception as e:
            logger.error(f"Error switching to iframe: {e}")
        
        # Log the page source to help with debugging
        try:
            page_html = self.browser.driver.page_source
            # Log just a snippet of the HTML to avoid overwhelming the logs
            logger.info(f"Lottery page HTML snippet: {page_html[:500]}...")
            
            # Look for lottery-related elements in the HTML
            if "st_campaign_button" in page_html:
                logger.info("Found 'st_campaign_button' class in page source")
            if "enter_event" in page_html:
                logger.info("Found 'enter_event' function reference in page source")
            if "Enter" in page_html:
                logger.info("Found 'Enter' text in page source")
        except Exception as e:
            logger.error(f"Error analyzing page source: {e}")
        
        # Find all lottery entry buttons based on the exact structure provided
        lottery_buttons = []
        
        # Approach 1: Find by class and onclick attribute (exact match to the provided HTML)
        logger.info("Looking for lottery buttons by class and onclick attribute...")
        buttons = self.browser.find_elements_safe(
            By.XPATH,
            "//a[contains(@class, 'st_campaign_button') and contains(@class, 'st_style_button') and contains(@onclick, 'enter_event')]"
        )
        if buttons:
            logger.info(f"Found {len(buttons)} lottery buttons by class and onclick attribute")
            lottery_buttons.extend(buttons)
            
            # Take a screenshot of the first button for debugging
            if buttons[0]:
                try:
                    self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", buttons[0])
                    self.browser.take_screenshot("found_lottery_button.png")
                except Exception as e:
                    logger.error(f"Error scrolling to button: {e}")
        
        # Approach 2: Find by text content "Enter"
        if not lottery_buttons:
            logger.info("Looking for lottery buttons by text content...")
            buttons = self.browser.find_elements_safe(
                By.XPATH,
                "//a[text()='Enter' or contains(text(), 'Enter')]"
            )
            if buttons:
                logger.info(f"Found {len(buttons)} lottery buttons by text content")
                lottery_buttons.extend(buttons)
        
        # Approach 3: Try the exact XPath provided by the user
        if not lottery_buttons:
            logger.info("Trying the exact XPath provided...")
            button = self.browser.find_element_safe(
                By.XPATH,
                "/html/body/div[1]/div[1]/main/div[2]/div/div[2]/form/div[1]/div[3]/div[6]/div[3]/a"
            )
            if button:
                logger.info("Found lottery button using the exact XPath")
                lottery_buttons.append(button)
        
        # Approach 4: Use JavaScript to find all enter buttons
        if not lottery_buttons:
            logger.info("Using JavaScript to find lottery buttons...")
            try:
                buttons = self.browser.driver.execute_script("""
                    var buttons = [];
                    
                    // Find all elements with onclick attribute containing enter_event
                    var elements = document.querySelectorAll('a[onclick*="enter_event"]');
                    for (var i = 0; i < elements.length; i++) {
                        buttons.push(elements[i]);
                    }
                    
                    // Find all elements with st_campaign_button class
                    var campaignButtons = document.querySelectorAll('.st_campaign_button.st_style_button');
                    for (var i = 0; i < campaignButtons.length; i++) {
                        if (campaignButtons[i].textContent.trim() === 'Enter') {
                            buttons.push(campaignButtons[i]);
                        }
                    }
                    
                    // Log what we found
                    console.log('Found ' + buttons.length + ' potential lottery buttons');
                    
                    // Return the array of buttons
                    return buttons;
                """)
                
                if buttons and len(buttons) > 0:
                    logger.info(f"Found {len(buttons)} lottery buttons using JavaScript")
                    lottery_buttons = buttons
            except Exception as e:
                logger.error(f"Error using JavaScript to find lottery buttons: {e}")
        
        # Log details about the buttons we found
        logger.info(f"Found a total of {len(lottery_buttons)} lottery buttons")
        
        # Extract event IDs from the onclick attributes
        lottery_info = []
        for button in lottery_buttons:
            try:
                onclick = button.get_attribute("onclick")
                if onclick and "enter_event" in onclick:
                    # Extract the event ID from the onclick attribute
                    # Format: enter_event(32810)
                    event_id = onclick.split("(")[1].split(")")[0]
                    logger.info(f"Found lottery with event ID: {event_id}")
                    
                    # Try to get the show name from nearby elements
                    show_name = "Unknown Show"
                    try:
                        # Look for a heading element above this button
                        parent = button
                        for _ in range(5):  # Look up to 5 levels up
                            parent = parent.find_element(By.XPATH, "..")
                            heading = parent.find_elements(By.XPATH, ".//h1 | .//h2 | .//h3 | .//h4")
                            if heading:
                                show_name = heading[0].text.strip()
                                break
                    except Exception:
                        pass
                    
                    lottery_info.append({
                        "button": button,
                        "event_id": event_id,
                        "show_name": show_name
                    })
            except Exception as e:
                logger.warning(f"Error extracting event ID: {e}")
        
        logger.info(f"Extracted info for {len(lottery_info)} lotteries")
        
        # Return the lottery information
        return lottery_info

    def enter_lottery(self, lottery_info):
        """Enter a specific lottery on the SocialToaster page.
        
        Args:
            lottery_info: Dictionary containing lottery information:
                - button: WebElement for the Enter button
                - event_id: ID of the lottery event
                - show_name: Name of the show
        """
        try:
            # Get the show name from the lottery_info
            show_name = lottery_info.get("show_name", "Unknown Show")
            event_id = lottery_info.get("event_id", "Unknown")
            logger.info(f"Attempting to enter lottery for: {show_name} (Event ID: {event_id})")
            
            # Get the button from the lottery_info
            enter_button = lottery_info.get("button")
            if not enter_button:
                logger.warning(f"Enter button not found for {show_name}")
                return False
            
            # Try to click the button using JavaScript first (more reliable)
            try:
                logger.info("Attempting to click button using JavaScript...")
                self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", enter_button)
                time.sleep(0.5)  # Give the page time to scroll
                self.browser.driver.execute_script("arguments[0].click();", enter_button)
                logger.info("Button clicked using JavaScript")
            except Exception as e:
                logger.warning(f"JavaScript click failed: {e}, trying regular click...")
                # Fall back to regular click if JavaScript fails
                try:
                    self.browser.click_element(enter_button)
                except Exception as click_error:
                    # Check if this is a "no such element" error, which might indicate the lottery was already entered
                    if "no such element" in str(click_error):
                        logger.info(f"Element not found error when clicking - lottery {event_id} may have already been entered")
                        # Take a screenshot for debugging
                        self.browser.take_screenshot(f"already_entered_lottery_{event_id}.png")
                        return True  # Consider this a success since we can't enter it again
                    else:
                        # Re-raise if it's a different error
                        raise
            return True
            
        except Exception as e:
            logger.error(f"Error entering lottery: {e}")
            self.browser.take_screenshot("lottery_entry_error.png")
            
            # Switch back to the main content
            try:
                self.browser.driver.switch_to.default_content()
            except Exception:
                pass
            
            return False

    def run_lottery_entries(self):
        """Run the full lottery entry process."""
        logger.info("Starting lottery entry process")
        
        try:
            # Set up the browser
            self.browser.setup_driver()
            
            # Log in
            if not self.login():
                logger.error("Login failed, aborting lottery entries")
                return False
            
            # Navigate to lotteries page
            if not self.navigate_to_lotteries():
                logger.error("Failed to navigate to lotteries page")
                return False
            
            # Get available lotteries
            lotteries = self.get_available_lotteries()
            
            if not lotteries:
                logger.warning("No lotteries found")
                return False
            
            # Enter each lottery
            success_count = 0
            for lottery in lotteries:
                if self.enter_lottery(lottery):
                    success_count += 1
                
                # Add a random delay between entries to appear more human-like
                #time.sleep(random.uniform(0, .5))
            
            logger.info(f"Completed lottery entries. Successful: {success_count}/{len(lotteries)}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error during lottery entry process: {e}")
            self.browser.take_screenshot("lottery_process_error.png")
            return False
            
        finally:
            # Clean up
            self.browser.close()
            logger.info("Lottery entry process finished")
