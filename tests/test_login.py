import pytest
import allure

from pages.login_page import LoginPage
from config.config import UserEmail, UserPassword
from pages.product_page import ProductPage


@allure.feature("UI Login")
@pytest.mark.ui
class TestLogin:


    @allure.story("Successful Login")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_successful_login(self, driver):

        with allure.step("Open login page"):

            page = LoginPage(driver).open()

        with allure.step("Login with valid credentials"):

            page.login(
                UserEmail,
                UserPassword
            )

        with allure.step("Validate redirect to notes page"):

            home = ProductPage(driver)

            assert home.wait_for_url_contains("notes/app")

        with allure.step("Validate dashboard loaded"):

            assert home.is_element_present(
                home.ADD_NOTE_BTN
            )


    @allure.story("Invalid Credentials")
    @allure.severity(allure.severity_level.NORMAL)
    def test_invalid_credentials_shows_error(self, driver):

        with allure.step("Open login page"):

            page = LoginPage(driver).open()

        with allure.step("Login with invalid credentials"):

            page.login(
                "invalid@nowhere.com",
                "WrongPass999!"
            )

        with allure.step("Validate error message displayed"):

            assert page.is_error_displayed()

            msg = page.get_error_message()

            allure.attach(
                msg,
                name="error_message",
                attachment_type=allure.attachment_type.TEXT
            )

            assert msg != ""


    @allure.story("Empty Login Fields")
    @allure.severity(allure.severity_level.MINOR)
    def test_empty_fields_blocked(self, driver):

        with allure.step("Open login page"):

            page = LoginPage(driver).open()

        with allure.step("Click login without entering data"):

            page.click_login()

        with allure.step("Validate user remains on login page"):

            assert page.is_on_login_page()


    @allure.story("Wrong Password")
    @allure.severity(allure.severity_level.NORMAL)
    def test_wrong_password_shows_error(self, driver):

        with allure.step("Open login page"):

            page = LoginPage(driver).open()

        with allure.step("Login with wrong password"):

            page.login(
                UserEmail,
                "CompletelyWrongPassword!"
            )

        with allure.step("Validate error displayed"):

            assert page.is_error_displayed()

            msg = page.get_error_message()

            allure.attach(
                msg,
                name="wrong_password_error",
                attachment_type=allure.attachment_type.TEXT
            )