"""
tests/test_ui_notes.py
Section 2.2 — UI Automation: note creation, DOM validation, UI performance.
Covers FR-02, FR-03, FR-08 | Scenarios TS-02, TS-03 | Cases TC-UI-02, TC-UI-03
"""
import time
import pytest
import allure
from pages.product_page import ProductPage

@allure.feature("UI — Notes Management")
@pytest.mark.ui
class TestUINotesCreation:

    @allure.story("TC-UI-02: Create note and verify it appears in UI")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_note_visible_in_ui(self, logged_in_driver):

        title = f"UI Note {int(time.time())}"
        desc = "Created by automated UI test."

        home = ProductPage(logged_in_driver)

        with allure.step("Create note"):
            home.create_note(
                title=title,
                description=desc,
                category="Home"
            )

        with allure.step("Verify note appears in UI"):
            assert home.is_note_in_ui(title), \
                f"Created note '{title}' not found in UI"
            
        home.delete_note(title)

    @allure.story("TC-UI-03: Note appears in DOM list without page reload")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_note_appears_in_dom_without_reload(self, logged_in_driver):
        """FR-03: After saving, note title must be present in DOM without manual refresh."""
        title = f"DOM Check {int(time.time())}"

        home = ProductPage(logged_in_driver)
        home.create_note(title=title, description="DOM update test",category="Home")

        time.sleep(2)

        with allure.step("Assert note is in DOM without page reload"):
            assert home.is_dom_updated_without_refresh(title), \
                f"Note '{title}' not visible in DOM after creation (no reload)"
            
        home.delete_note(title)

    @allure.story("TC-UI-03b: Note title matches exactly in notes list")
    @allure.severity(allure.severity_level.NORMAL)
    def test_note_title_in_list(self, logged_in_driver):
        """FR-02 & FR-03: Note title visible in rendered notes list."""
        title = f"Title Match {int(time.time())}"

        home = ProductPage(logged_in_driver)
        home.create_note(title=title, description="Checking title in list", category="Home")
        home.wait_for_dom_ready()

        with allure.step("Assert note title is in notes list"):
            all_titles = home.get_all_note_titles()
            allure.attach(str(all_titles), name="notes_in_ui",
                          attachment_type=allure.attachment_type.TEXT)
            assert title in all_titles, \
                f"'{title}' not found in UI list: {all_titles}"
        
        home.delete_note(title)

    @allure.story("TC-UI-04: Multiple notes created — all appear in list")
    @allure.severity(allure.severity_level.NORMAL)
    def test_multiple_notes_all_visible(self, logged_in_driver):
        """FR-02 & FR-03: Creating 3 notes — all 3 appear in the notes list."""
        home = ProductPage(logged_in_driver)
        titles = [f"Multi Note {i} {int(time.time())}" for i in range(3)]

        for title in titles:
            home.create_note(title=title, description=f"Note body for {title}", category="Home")
            home.wait_for_dom_ready()
            time.sleep(0.5)

        all_titles = home.get_all_note_titles()
        for title in titles:
            assert title in all_titles, \
                f"Note '{title}' missing from UI list: {all_titles}"
            
        for title in titles:
            home.delete_note(title)

    @allure.story("TC-UI-05: UI page load timing within acceptable limit")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.slow
    def test_page_load_performance(self, logged_in_driver):
        """Section 3.5 — Measure UI navigation and DOM-ready timings."""
        home = ProductPage(logged_in_driver)

        timing = home.get_navigation_timing()
        page_load_sec = round(timing["page_load_ms"] / 1000, 3)
        dom_ready_sec = round(timing["dom_ready_ms"] / 1000, 3)

        allure.attach(
            f"Page load : {page_load_sec}s\nDOM ready  : {dom_ready_sec}s",
            name="ui_timing", attachment_type=allure.attachment_type.TEXT
        )
        assert page_load_sec < 20.0, f"Page load too slow: {page_load_sec}s"
        assert dom_ready_sec < 10.0,  f"DOM ready too slow: {dom_ready_sec}s"

    @pytest.mark.delete
    @allure.story("Delete Note From UI")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_note_ui(self, logged_in_driver):

        title = f"Delete Test {int(time.time())}"

        home = ProductPage(logged_in_driver)

        # Create note first
        home.create_note(
            category="Home",
            title=title,
            description="Delete note test"
        )

        # Check note created
        assert home.is_note_in_ui(title)

        # Delete note
        home.delete_note(title)

        home.wait_for_dom_ready()

        # Verify note removed
        assert not home.is_note_in_ui(title), \
            f"Note '{title}' still visible after delete"