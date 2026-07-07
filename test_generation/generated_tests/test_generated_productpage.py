

from pages.product_page import (
            ProductPage
        )
import pytest
import allure


@allure.feature("Product Page - Notes Management")
@allure.story("User can create, view, and delete notes on product page")
class TestProductPageNotes:

    @allure.title("Create a new note with valid data")
    def test_create_note_successfully(self, logged_in_driver):
        """
        Verify that a user can successfully create a new note
        with title, description, and category.
        """
        page = ProductPage(logged_in_driver)
        
        # Define test data
        note_title = "Test Note Title"
        note_description = "This is a test note description for automation."
        note_category = "General"
        
        # Create note
        page.enter_title(note_title)
        page.enter_description(note_description)
        page.select_category(note_category)
        page.click_save()
        
        # Verify success
        assert page.is_success_banner_visible(), "Success banner should be visible after saving note"
        assert page.get_success_message() == "Note saved successfully", "Success message should match expected"
        assert page.is_note_in_ui(note_title), f"Note with title '{note_title}' should appear in the list"
        assert page.get_note_count() == 1, "Note count should be 1 after creating one note"

    @allure.title("Delete an existing note")
    def test_delete_note_successfully(self, logged_in_driver):
        """
        Verify that a user can successfully delete an existing note.
        """
        page = ProductPage(logged_in_driver)
        
        # Pre-create a note to delete
        note_title = "Note to Delete"
        page.enter_title(note_title)
        page.enter_description("This note will be deleted.")
        page.select_category("General")
        page.click_save()
        
        # Ensure note exists
        assert page.is_note_in_ui(note_title), "Note should exist before deletion"
        initial_count = page.get_note_count()
        
        # Delete the note
        page.click_delete_note(note_title)
        page.click_confirm_delete()
        
        # Verify deletion
        assert page.is_success_banner_visible(), "Success banner should appear after deletion"
        assert page.get_success_message() == "Note deleted successfully", "Deletion success message should match"
        assert not page.is_note_in_ui(note_title), f"Note '{note_title}' should no longer exist in UI"
        assert page.get_note_count() == initial_count - 1, "Note count should decrease by 1 after deletion"

    @allure.title("Verify empty state when no notes exist")
    def test_empty_notes_list(self, logged_in_driver):
        """
        Verify that the notes list shows empty state when no notes are present.
        """
        page = ProductPage(logged_in_driver)
        
        # Ensure no notes exist (cleanup if needed)
        all_titles = page.get_all_note_titles()
        for title in all_titles:
            page.click_delete_note(title)
            page.click_confirm_delete()
        
        # Verify empty state
        assert page.is_list_empty(), "Notes list should be empty"
        assert page.get_note_count() == 0, "Note count should be 0 when no notes exist"

    @allure.title("Create multiple notes and verify count")
    def test_create_multiple_notes(self, logged_in_driver):
        """
        Verify that multiple notes can be created and counted correctly.
        """
        page = ProductPage(logged_in_driver)
        
        # Define multiple notes
        notes = [
            {"title": "First Note", "description": "First test note", "category": "Work"},
            {"title": "Second Note", "description": "Second test note", "category": "Personal"},
            {"title": "Third Note", "description": "Third test note", "category": "General"}
        ]
        
        # Create notes
        for note in notes:
            page.enter_title(note["title"])
            page.enter_description(note["description"])
            page.select_category(note["category"])
            page.click_save()
        
        # Verify all notes exist
        assert page.get_note_count() == len(notes), f"Note count should be {len(notes)}"
        for note in notes:
            assert page.is_note_in_ui(note["title"]), f"Note '{note['title']}' should exist in UI"

    @allure.title("Verify navigation timing is recorded")
    def test_navigation_timing_recorded(self, logged_in_driver):
        """
        Verify that navigation timing information is available on the product page.
        """
        page = ProductPage(logged_in_driver)
        
        # Wait for page to load and check timing
        timing = page.get_navigation_timing()
        
        assert timing is not None, "Navigation timing should be available"
        assert isinstance(timing, dict), "Navigation timing should be a dictionary"
        assert "load_time" in timing, "Navigation timing should include load_time"
        assert timing["load_time"] > 0, "Load time should be greater than 0"

    @allure.title("Verify DOM updates without refresh after note creation")
    def test_dom_updated_without_refresh(self, logged_in_driver):
        """
        Verify that the DOM is updated dynamically after creating a note without requiring a page refresh.
        """
        page = ProductPage(logged_in_driver)
        
        # Create a note
        note_title = "Dynamic Update Test"
        page.enter_title(note_title)
        page.enter_description("Testing DOM update")
        page.select_category("General")
        page.click_save()
        
        # Verify DOM was updated without refresh
        assert page.is_dom_updated_without_refresh(), "DOM should be updated without requiring a refresh"
        assert page.is_note_in_ui(note_title), "New note should appear in UI immediately"
