from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from config.config import BASE_UI_URL
import logging

logger = logging.getLogger(__name__)

class LoginPage(BasePage):

    Email_Primary=(By.CSS_SELECTOR, "input[data-testid='login-email']")
    Email_fallback=[(By.XPATH, "//input[@type='email']"), (By.NAME, "email")]

    Pass_Primary=(By.CSS_SELECTOR, "input[data-testid='login-password']")
    Pass_fallback=[(By.XPATH, "//input[@type='password']"), (By.NAME, "password")]

    Login_Button_Primary=(By.CSS_SELECTOR, "button[data-testid='login-submit']")
    Login_Button_fallback=[(By.XPATH, "//button[contains(text(),'Login')]"),
                         (By.CSS_SELECTOR, "button[type='submit']")]
    
    ERROR_MSG         = (By.CSS_SELECTOR, "[data-testid='alert-message']")
    REGISTER_LINK     = (By.CSS_SELECTOR, "a[href*='register']")


    def open(self):
        self.driver.get(BASE_UI_URL)
        logger.info("Navigated to Login Page")
        return self
    
    def enter_email(self, email):
        el = self.enter_text(self.Email_Primary, email)
        return self
    
    def enter_password(self, password):
        el = self.enter_text(self.Pass_Primary, password)
        return self
    
    def click_login(self):

        self.safe_click(

            self.Login_Button_Primary,

            element_name=
            "LOGIN_BUTTON"
        )

        return self
    
    def login(self, email, password):
        self.enter_email(email)
        self.enter_password(password)
        self.click_login()
        logger.info("Login attempted with email: %s", email)

    def get_error_message(self):
        return self.get_text(self.ERROR_MSG)
    
    def is_error_displayed(self):
        return self.is_element_displayed(self.ERROR_MSG)
        
    def is_on_login_page(self):
        return self.is_element_displayed(self.Login_Button_Primary)