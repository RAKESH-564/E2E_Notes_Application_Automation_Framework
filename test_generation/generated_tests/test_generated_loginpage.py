import pytest
import allure

from pages.login_page import (
    LoginPage
)

@allure.feature("Login")
@allure.story("User Login")
def test_successful_login(driver):
    """
    Test that a user can successfully log in with valid credentials.
    """
    with allure.step("Open login page"):
        login_page = LoginPage(driver)
        login_page.open()

    with allure.step("Enter valid credentials and submit"):
        login_page.login(UserEmail, UserPassword)

    with allure.step("Verify user is redirected away from login page"):
        assert not login_page.is_on_login_page(), "User should be redirected after successful login"


@allure.feature("Login")
@allure.story("Invalid Login Attempts")
def test_login_with_invalid_email(driver):
    """
    Test that login fails with an invalid email format.
    """
    with allure.step("Open login page"):
        login_page = LoginPage(driver)
        login_page.open()

    with allure.step("Enter invalid email and valid password"):
        login_page.enter_email("invalid-email")
        login_page.enter_password(UserPassword)
        login_page.click_login()

    with allure.step("Verify error message is displayed"):
        assert login_page.is_error_displayed(), "Error message should be displayed for invalid email"
        error_message = login_page.get_error_message()
        assert "valid email" in error_message.lower() or "invalid" in error_message.lower(), \
            f"Expected validation error, got: {error_message}"


@allure.feature("Login")
@allure.story("Invalid Login Attempts")
def test_login_with_wrong_password(driver):
    """
    Test that login fails with incorrect password.
    """
    with allure.step("Open login page"):
        login_page = LoginPage(driver)
        login_page.open()

    with allure.step("Enter valid email and wrong password"):
        login_page.enter_email(UserEmail)
        login_page.enter_password("WrongPassword123!")
        login_page.click_login()

    with allure.step("Verify error message is displayed"):
        assert login_page.is_error_displayed(), "Error message should be displayed for wrong password"
        error_message = login_page.get_error_message()
        assert "password" in error_message.lower() or "incorrect" in error_message.lower() or "invalid" in error_message.lower(), \
            f"Expected authentication error, got: {error_message}"


@allure.feature("Login")
@allure.story("Empty Credentials")
def test_login_with_empty_credentials(driver):
    """
    Test that login fails when both email and password fields are empty.
    """
    with allure.step("Open login page"):
        login_page = LoginPage(driver)
        login_page.open()

    with allure.step("Attempt login without entering credentials"):
        login_page.click_login()

    with allure.step("Verify error message is displayed"):
        assert login_page.is_error_displayed(), "Error message should be displayed for empty fields"
        error_message = login_page.get_error_message()
        assert "required" in error_message.lower() or "empty" in error_message.lower() or "enter" in error_message.lower(), \
            f"Expected field validation error, got: {error_message}"


@allure.feature("Login")
@allure.story("Empty Credentials")
def test_login_with_empty_password(driver):
    """
    Test that login fails when password field is empty.
    """
    with allure.step("Open login page"):
        login_page = LoginPage(driver)
        login_page.open()

    with allure.step("Enter valid email but leave password empty"):
        login_page.enter_email(UserEmail)
        login_page.click_login()

    with allure.step("Verify error message is displayed"):
        assert login_page.is_error_displayed(), "Error message should be displayed for empty password"
        error_message = login_page.get_error_message()
        assert "password" in error_message.lower() or "required" in error_message.lower(), \
            f"Expected password validation error, got: {error_message}"