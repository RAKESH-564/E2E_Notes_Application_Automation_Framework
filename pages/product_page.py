import time

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
import logging
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException

logger = logging.getLogger(__name__)

class ProductPage(BasePage):

    ADD_NOTE_BTN       = (By.CSS_SELECTOR, "button[data-testid='add-new-note']")
    NOTE_CATEGORY      = (By.CSS_SELECTOR, "select[data-testid='note-category']")
    NOTE_TITLE         = (By.CSS_SELECTOR, "input[data-testid='note-title']")
    NOTE_DESCRIPTION   = (By.CSS_SELECTOR, "textarea[data-testid='note-description']")
    SAVE_NOTE_BTN      = (By.CSS_SELECTOR, "button[data-testid='note-submit']")
    # SUCCESS_BANNER     = (By.CSS_SELECTOR, "[data-testid='alert-message']")
    NOTE_CARDS         = (By.CSS_SELECTOR, "[data-testid='note-card']")
    NOTE_CARD_TITLE    = (By.CSS_SELECTOR, "[data-testid='note-card-title']")
    DELETE_NOTE_BTN    = (By.CSS_SELECTOR, "button[data-testid='note-delete']")
    CONFIRM_DELETE_BTN = (By.CSS_SELECTOR, "button[data-testid='note-delete-confirm']")
    LOGOUT_BTN         = (By.CSS_SELECTOR, "a[data-testid='logout']")
    EMPTY_NOTE_MSG     = (By.CSS_SELECTOR, "[data-testid='notes-empty']")

    Add_Note_Btn_Fallback = [
        (By.XPATH, "//a[contains(text(),'Add Note')]"),
        (By.CSS_SELECTOR, "button[data-testid='add-note']"),
    ]

    def click_add_note(self):

        self.js_scroll_to(
            self.ADD_NOTE_BTN
        )

        self.safe_click(

            self.ADD_NOTE_BTN,

            element_name=
            "ADD_NOTE_BUTTON"
        )

        logger.info(
            "Clicked on "
            "Add Note button"
        )

        return self
    
    def select_category(self, category="Home"):
        dropdown_element = self.wait_for_visible(self.NOTE_CATEGORY)
        select = Select(dropdown_element)
        if category:
            select.select_by_visible_text(category)
            # ↑ "Home" matches <option>Home</option> in the dropdown
            logger.info(f"Selected category: {category}")
        else:
            # If category is None, just leave default selected
            logger.info("No category specified — using default")
        
        return self        

    
    def enter_title(self, title):
        self.enter_text(self.NOTE_TITLE, title)
        logger.info("Entered note title: %s", title)
        return self
    
    def enter_description(self, description):
        self.enter_text(self.NOTE_DESCRIPTION, description)
        logger.info("Entered note description")
        return self
    
    def click_save(self):

        self.js_scroll_to(
            self.SAVE_NOTE_BTN
        )

        self.safe_click(

            self.SAVE_NOTE_BTN,

            element_name=
            "SAVE_NOTE_BUTTON"
        )

        logger.info(
            "Clicked on Save Note button"
        )

        return self
    

    def create_note(self, category, title, description):

            self.click_add_note()

            self.select_category(category)

            self.enter_title(title)

            self.enter_description(description)

            self.click_save()

            self.driver.refresh()  # Force refresh to ensure UI updates with new note

            self.wait_for_dom_ready()

            time.sleep(2)

            # Wait until newly created note title appears
            locator = (
                By.XPATH,
                f"//*[@data-testid='note-card-title' and normalize-space(text())='{title}']"
            )

            WebDriverWait(self.driver, 10).until(
                lambda d: d.find_element(*locator).is_displayed()
            )

            logger.info("Note created successfully: %s", title)

            return self
    
    def is_success_banner_visible(self, timeout: int = 10) -> bool:
        return self.is_element_visible(self.SUCCESS_BANNER, timeout)
    
    def get_success_message(self):
        return self.get_text(self.SUCCESS_BANNER)
    
    def get_all_note_titles(self):

        self.wait_for_dom_ready()
        titles = []
        for _ in range(3):
            try:
                elements = self.get_elements(
                    self.NOTE_CARD_TITLE
                )

                titles = [
                    el.text.strip()
                    for el in elements
                ]

                break

            except Exception:

                self.wait_for_dom_ready()

        return titles

    def is_note_in_ui(self,title,timeout=15):

        locator = (
            By.XPATH,
            f"//*[@data-testid='note-card-title' and contains(text(),'{title}')]"
        )

        try:
            self.wait_for_visible(
                locator,
                timeout
            )
            return True
        except Exception:

            return False

    def get_note_count(self):

        self.wait_for_dom_ready()
        for _ in range(3):
            try:
                cards = self.get_elements(
                    self.NOTE_CARDS
                )
                return len(cards)
            except Exception:
                self.wait_for_dom_ready()
        return 0

    def is_list_empty(self):
        return (self.is_element_displayed(self.EMPTY_NOTE_MSG) or self.get_note_count() == 0)
    
    def logout(self):
        self.safe_click(self.LOGOUT_BTN)
        logger.info("Clicked on Logout button")
        return self
    
    def is_dom_updated_without_refresh(self, title: str, timeout: int = 10) -> bool:
        """Confirm the note title appears in DOM without a page reload."""
        locator = (By.XPATH,
                   f"//*[@data-testid='note-card-title' and contains(text(),'{title}')]")
        try:
            self.wait_for_visible(
                locator,
                timeout
            )
            return True
        except Exception:
            return False
    
    def click_delete_note(self):

        self.js_scroll_to(self.DELETE_NOTE_BTN)

        try:
            self.retry_click(self.DELETE_NOTE_BTN)
        except Exception:
            self.js_click(self.DELETE_NOTE_BTN)

        return self


    def click_confirm_delete(self):

        self.js_scroll_to(self.CONFIRM_DELETE_BTN)

        try:
            self.retry_click(self.CONFIRM_DELETE_BTN)
        except Exception:
            self.js_click(self.CONFIRM_DELETE_BTN)

        return self


    def delete_note(
        self,
        title,
        retries=3
    ):

        old_count = (
            self.get_note_count()
        )

        delete_btn = (

            By.XPATH,

            f"""
            //div[@data-testid='note-card']
            [.//*[@data-testid='note-card-title'
            and normalize-space(text())='{title}']]
            //button[@data-testid='note-delete']
            """
        )

        for attempt in range(
            retries
        ):

            try:

                self.wait_for_dom_ready()

                self.js_scroll_to(
                    delete_btn
                )

                try:

                    self.retry_click(
                        delete_btn
                    )

                except Exception:

                    self.js_click(
                        delete_btn
                    )

                self.click_confirm_delete()

                WebDriverWait(
                    self.driver,
                    15
                ).until(

                    lambda d:

                    len(

                        d.find_elements(

                            *self.NOTE_CARDS
                        )

                    ) < old_count
                )

                return self

            except (
                StaleElementReferenceException
            ):

                print(
                    f"[STALE DELETE RETRY] "
                    f"{attempt + 1}/"
                    f"{retries}"
                )

                time.sleep(2)

        return self