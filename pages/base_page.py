
from asyncio.log import logger
import time
import os

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.config import TimeOut

from utils.healing_engine import (
    HealingEngine
)

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException
)

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait=WebDriverWait(driver, TimeOut)
        self.healing_engine = (HealingEngine())

    def wait_for_element(
        self,
        locator,
        element_name=None
    ):

        try:

            return self.wait.until(

                EC.presence_of_element_located(
                    locator
                )
            )

        except Exception:

            print(
                f"[HEALING] "
                f"Trying to heal: "
                f"{element_name}"
            )

            if element_name:

                healed_element = (
                    self.healing_engine
                    .heal_locator(

                        self.driver,

                        element_name
                    )
                )

                if healed_element:

                    return healed_element

            raise
    
    def wait_for_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))
    
    def click(self, locator):
        element = self.wait_for_clickable(locator)
        element.click()

    def enter_text(self, locator, text):
        element = self.wait_for_element(locator)
        element.clear()
        element.send_keys(text)
    
    def get_text(self, locator):
        element = self.wait_for_element(locator)
        return element.text
    
    def is_element_displayed(self, locator):
        try:
            return self.wait_for_element(locator).is_displayed()
        except:
            return False
        
    def get_elements(self, locator):
        return self.wait.until(EC.presence_of_all_elements_located(locator))
    
    def wait_for_url_contains(self, text):
        return self.wait.until(lambda d: text in d.current_url)
    
    def is_element_present(self, locator):
        try:
            self.wait_for_element(locator)
            return True
        except:
            return False
        
    def wait_for_dom_ready(self, timeout: int = 15):
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def wait_for_visible(self, locator, timeout=None):
        """
        Waits until element is VISIBLE on screen.

        Difference from your existing methods:
          wait_for_element()   → just checks element EXISTS in DOM (could be hidden)
          wait_for_clickable() → checks visible AND enabled (ready to interact)
          wait_for_visible()   → checks element is VISIBLE (user can see it)

        ProductPage.select_category() calls this before wrapping in Select().
        We need visible (not just present) because a hidden <select>
        cannot be interacted with even if it exists in the DOM.

        timeout=None means use your default TimeOut from config.
        """
        wait = WebDriverWait(self.driver, timeout) if timeout else self.wait
        return wait.until(EC.visibility_of_element_located(locator))

    def is_element_visible(self, locator, timeout=5):
        """
        Returns True/False — never raises an exception.

        Difference from your existing is_element_displayed():
          is_element_displayed() uses wait_for_element() first
            → waits full TimeOut for element to EXIST, then checks displayed
            → slow when element genuinely doesn't exist

          is_element_visible() uses visibility condition directly
            → uses a short custom timeout (default 5s)
            → returns False quickly when element isn't there
            → safe to use in assertions like:
               assert home.is_element_visible(banner) → won't hang

        Used by: is_success_banner_visible(), is_dom_updated_without_refresh()
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except:
            return False

    def js_click(self, locator):
        """
        Clicks an element using JavaScript instead of Selenium's normal click.

        WHY you need this:
          Normal click → Selenium moves mouse to element coordinates → clicks
          If ANYTHING is on top of the element (overlay, spinner, another div)
          → ElementClickInterceptedException

          JS click → tells the browser directly "click this element"
          → bypasses any overlapping elements completely
          → works even when element is partially off-screen

        Use this when:
          - You get ElementClickInterceptedException
          - Button is covered by a loading spinner
          - Element is in a weird position
        """
        element = self.wait_for_element(locator)
        self.driver.execute_script("arguments[0].click();", element)
        # arguments[0] refers to the element passed in
        # This is standard JS executor syntax in Selenium

    def js_scroll_to(self, locator):
        """
        Scrolls the page until the element is centered on screen.

        WHY you need this:
          Selenium can only click elements that are in the VIEWPORT
          (the visible area of the browser window).
          If a button is below the fold (you'd need to scroll to see it),
          clicking it throws ElementClickInterceptedException or MoveTargetOutOfBoundsException.

          scrollIntoView({block: 'center'}) puts it in the middle of screen
          which is better than 'start' (top) because top might be hidden
          behind a fixed navigation bar.

        Always call this BEFORE clicking elements that might be off-screen.
        """
        element = self.wait_for_element(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element
        )
        # Small pause after scroll — let the page settle
        # Without this, the click can fire before scroll animation finishes
        time.sleep(0.3)

    def retry_click(self, locator, retries=3, delay=1):
        """
        Tries to click an element up to `retries` times.
        Waits `delay` seconds between each attempt.

        WHY you need this:
          Some UI elements are temporarily unclickable due to:
          - Page still rendering
          - Animation in progress
          - React/Angular re-rendering the component
          These are "transient" failures — they pass on retry.

          retry_click separates transient failures (flakiness)
          from real failures (element genuinely doesn't exist).

          If all 3 attempts fail → raises the last exception
          → test fails with a real error, not silently swallowed.

        Flow:
          Attempt 1 → fails → wait 1s → Attempt 2 → fails → wait 1s → Attempt 3
          If attempt 3 also fails → raise exception → test fails
        """
        last_error = None
        for attempt in range(1, retries + 1):
            try:
                self.safe_click(locator)
                return  # clicked successfully — stop here
            except Exception as e:
                last_error = e
                logger.warning(
                    f"[retry_click] Attempt {attempt}/{retries} failed: {e}"
                )
                if attempt < retries:
                    time.sleep(delay)

        # All attempts exhausted — raise last error so test fails properly
        raise last_error

    def get_navigation_timing(self) -> dict:
        """
        Reads browser's built-in performance data to measure page load speed.

        HOW IT WORKS:
          Every browser tracks timing data automatically in window.performance.timing
          It records timestamps (in milliseconds since epoch) for key events:

          navigationStart          → browser started loading the page
          domContentLoadedEventEnd → HTML parsed, DOM tree built (no images yet)
          loadEventEnd             → EVERYTHING done (images, CSS, JS, fonts)

          We subtract navigationStart from each to get elapsed time since load began.

          Example:
            navigationStart          = 1714900000000  (ms)
            domContentLoadedEventEnd = 1714900001500  (ms)
            dom_ready_ms = 1500ms = 1.5 seconds to build DOM

        WHAT THE TEST DOES WITH IT:
          timing = home.get_navigation_timing()
          page_load_sec = round(timing["page_load_ms"] / 1000, 3)
          dom_ready_sec = round(timing["dom_ready_ms"] / 1000, 3)
          assert page_load_sec < 10.0

        Returns dict with keys:
          dom_ready_ms : milliseconds until DOM was ready
          page_load_ms : milliseconds until full page loaded
        """
        return self.driver.execute_script("""
            var t = window.performance.timing;
            return {
                dom_ready_ms: t.domContentLoadedEventEnd - t.navigationStart,
                page_load_ms: t.loadEventEnd - t.navigationStart
            };
        """)

    def take_screenshot(self, name="screenshot"):
        """
        Saves a screenshot of current browser state to reports/screenshots/.
        Called automatically by conftest when any test fails.
        Returns the file path so it can be attached to Allure report.
        """
        folder = "reports/screenshots"
        os.makedirs(folder, exist_ok=True)
        path = f"{folder}/{name}_{int(time.time())}.png"
        self.driver.save_screenshot(path)
        logger.info(f"Screenshot saved: {path}")
        return path
    

    def safe_click(
        self,
        locator,
        element_name=None,
        retries=3
    ):

        last_error = None

        for attempt in range(
            retries
        ):

            try:

                element = (
                    self.wait_for_clickable(
                        locator
                    )
                )

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    element
                )

                time.sleep(1)

                element.click()

                return

            except Exception as e:

                last_error = e

                print(
                    f"[CLICK FAILED] "
                    f"Attempt "
                    f"{attempt + 1}/"
                    f"{retries}"
                )

                time.sleep(1)

        # -----------------------
        # Healing
        # -----------------------
        if element_name:

            print(
                f"[HEALING] "
                f"{element_name}"
            )

            healed = (
                self.healing_engine
                .heal_locator(

                    self.driver,

                    element_name
                )
            )

            if healed:

                try:

                    healed.click()

                    print(
                        "[HEAL SUCCESS]"
                    )

                    return

                except Exception:

                    self.driver.execute_script(
                        "arguments[0].click();",
                        healed
                    )

                    print(
                        "[JS HEAL SUCCESS]"
                    )

                    return

        raise last_error