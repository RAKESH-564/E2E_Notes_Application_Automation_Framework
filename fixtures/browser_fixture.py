import pytest
import os
import allure

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from api_client.notes_client import NotesAPIClient
from agents.flaky_test_agent import FlakyTestAgent


flaky_agent = FlakyTestAgent()


# --------------------------------
# Selenium Driver Fixture
# --------------------------------
@pytest.fixture
def driver():

    options = webdriver.ChromeOptions()

    # -----------------------------
    # Browser Settings
    # -----------------------------
    options.add_argument(
        "--start-maximized"
    )

    options.add_argument(
        "--window-size=1920,1080"
    )

    options.add_argument(
        "--disable-notifications"
    )

    options.add_argument(
        "--disable-popup-blocking"
    )

    options.add_argument(
        "--disable-dev-shm-usage"
    )

    options.add_argument(
        "--disable-extensions"
    )

    options.add_argument(
        "--disable-background-networking"
    )

    options.add_argument(
        "--disable-background-timer-throttling"
    )

    options.add_argument(
        "--disable-renderer-backgrounding"
    )

    options.add_argument(
        "--disable-features=VizDisplayCompositor"
    )

    options.add_argument(
        "--disable-features=Translate"
    )

    options.add_argument(
        "--disable-infobars"
    )

    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    options.add_argument(
        "--disable-gpu"
    )

    options.add_argument(
        "--no-sandbox"
    )

    # -----------------------------
    # Block Ads / Popups
    # -----------------------------
    prefs = {

        "profile.default_content_setting_values.notifications": 2,

        "profile.default_content_settings.popups": 0,

        "credentials_enable_service": False,

        "profile.password_manager_enabled": False,

        "profile.managed_default_content_settings.images": 2
    }

    options.add_experimental_option(
        "prefs",
        prefs
    )

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )

    options.add_experimental_option(
        "useAutomationExtension",
        False
    )

    use_remote = os.getenv(
        "REMOTE",
        "false"
    ).lower() == "true"

    # -----------------------------
    # Remote Docker Selenium Grid
    # -----------------------------
    if use_remote:

        driver = webdriver.Remote(

            command_executor=
            "http://localhost:4444/wd/hub",

            options=options
        )

    else:

        service = Service(
            ChromeDriverManager()
            .install()
        )

        driver = webdriver.Chrome(
            service=service,
            options=options
        )

    # -----------------------------
    # Hide Selenium Detection
    # -----------------------------
    driver.execute_script(
        """
        Object.defineProperty(
            navigator,
            'webdriver',
            {
                get: () => undefined
            }
        )
        """
    )

    driver.implicitly_wait(5)

    driver.set_page_load_timeout(60)

    driver.set_script_timeout(60)

    yield driver

    try:

        driver.quit()

    except Exception:

        pass


# --------------------------------
# Logged In Driver Fixture
# --------------------------------
@pytest.fixture
def logged_in_driver(driver):

    from pages.login_page import LoginPage
    from config.config import (
        UserEmail,
        UserPassword
    )

    page = LoginPage(driver).open()

    page.login(
        UserEmail,
        UserPassword
    )

    page.wait_for_url_contains(
        "notes/app"
    )

    return driver


# --------------------------------
# API Client Fixture
# --------------------------------
@pytest.fixture
def api_client():

    from config.config import (
        UserEmail,
        UserPassword
    )

    client = NotesAPIClient()

    client.login(
        email=UserEmail,
        password=UserPassword
    )

    return client


# --------------------------------
# Screenshot On Failure
# --------------------------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item,
    call,
):

    outcome = yield

    report = outcome.get_result()

    if (
        report.when == "call"
        and report.failed
    ):

        driver = item.funcargs.get(
            "driver"
        )

        if driver:

            screenshots_dir = (
                "reports/screenshots"
            )

            os.makedirs(
                screenshots_dir,
                exist_ok=True
            )

            screenshot_path = (
                f"{screenshots_dir}/"
                f"{item.name}.png"
            )

            driver.save_screenshot(
                screenshot_path
            )

            allure.attach.file(
                screenshot_path,
                name="Failure Screenshot",
                attachment_type=
                allure.attachment_type.PNG
            )

            # ------------------------
            # Flaky Test Analysis
            # ------------------------
            try:

                flaky_agent.save_failure(

                    test_name=
                    item.name,

                    error_message=
                    call.excinfo.value
                )

            except Exception as e:

                print(
                    "[FLAKY AGENT ERROR]",
                    str(e)
                )