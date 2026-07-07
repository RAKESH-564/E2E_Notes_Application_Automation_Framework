

import time
import pytest
import allure

from pages.product_page import ProductPage
from api_client.notes_client import NotesAPIClient

from config.config import (
    UserEmail,
    UserPassword
)


@allure.feature("E2E UI API")
@pytest.mark.e2e
class TestUIToAPI:


    @allure.story("Create Note In UI Check In API")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_ui_note_in_api(self, logged_in_driver):

        title = f"E2E {int(time.time())}"

        description = "Created in UI"

        home = ProductPage(logged_in_driver)

        with allure.step("Create note using UI"):

            home.create_note(
                title=title,
                description=description,
                category="Home"
            )

        home.wait_for_dom_ready()

        with allure.step("Validate note exists in UI"):

            assert home.is_note_in_ui(title)

        api = NotesAPIClient()

        with allure.step("Login using API"):

            api.login(
                UserEmail,
                UserPassword
            )

        with allure.step(
            "Validate UI note exists in API"
        ):

            note = None

            for attempt in range(5):

                response = (
                    api.get_notes()
                )

                note = (
                    api.find_note_in_list(
                        response,
                        title
                    )
                )

                if note:

                    print(
                        f"[SYNC SUCCESS] "
                        f"Note found in API "
                        f"on attempt "
                        f"{attempt + 1}"
                    )

                    break

                print(
                    f"[SYNC RETRY] "
                    f"Attempt "
                    f"{attempt + 1}"
                )

                time.sleep(2)

            allure.attach(
                str(note),
                name="api_note_data",
                attachment_type=
                allure.attachment_type.JSON
            )

            assert note is not None, (
                f"Note '{title}' "
                f"not found in API "
                f"after retries"
            )

            assert (
                note["title"]
                == title
            )

            assert (
                note["description"]
                == description
            )

        home.delete_note(title)


    @allure.story("Check UI API Full Data")
    @allure.severity(allure.severity_level.NORMAL)
    def test_ui_api_data_match(self, logged_in_driver):

        title = f"Match {int(time.time())}"

        description = "Checking full data"

        category = "Work"

        home = ProductPage(logged_in_driver)

        with allure.step("Create note in UI"):

            home.create_note(
                title=title,
                description=description,
                category=category
            )

        api = NotesAPIClient()

        with allure.step("Login using API"):

            api.login(
                UserEmail,
                UserPassword
            )
        
        time.sleep(2)

        with allure.step("Get notes from API"):

            response = api.get_notes()

        with allure.step("Validate note data"):

            note = api.find_note_in_list(
                response,
                title
            )

            allure.attach(
                str(note),
                name="matched_note",
                attachment_type=allure.attachment_type.JSON
            )

            assert note is not None

            assert note["title"] == title

            assert note["description"] == description

            assert "id" in note

        home.delete_note(title)


    @allure.story("Check Note Id")
    @allure.severity(allure.severity_level.NORMAL)
    def test_note_id_present(self, logged_in_driver):

        title = f"ID {int(time.time())}"

        home = ProductPage(logged_in_driver)

        with allure.step("Create note in UI"):

            home.create_note(
                category="Home",
                title=title,
                description="Id check"
            )

        api = NotesAPIClient()

        with allure.step("Login using API"):

            api.login(
                UserEmail,
                UserPassword
            )

        with allure.step("Fetch notes list"):

            response = api.get_notes()

        with allure.step("Validate note id exists"):

            note = api.find_note_in_list(
                response,
                title
            )

            assert note is not None

            assert "id" in note

            assert note["id"] != ""

        home.delete_note(title)


@allure.feature("E2E UI API")
@pytest.mark.e2e
class TestAPIToUI:


    @allure.story("Delete Using API Check UI")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_api_delete_reflects_in_ui(self, logged_in_driver):

        title = f"Delete {int(time.time())}"

        home = ProductPage(logged_in_driver)

        with allure.step("Create note using UI"):

            home.create_note(
                category="Home",
                title=title,
                description="Delete test"
            )

        with allure.step("Validate note exists in UI"):

            assert home.is_note_in_ui(title)

        api = NotesAPIClient()

        with allure.step("Login using API"):

            api.login(
                UserEmail,
                UserPassword
            )

        with allure.step("Fetch notes from API"):

            response = api.get_notes()

            note = api.find_note_in_list(
                response,
                title
            )

            assert note is not None

            note_id = note["id"]

        with allure.step("Delete note using API"):

            delete_response = api.delete_note(
                note_id
            )

            assert delete_response.status_code in [200, 204]

        with allure.step("Refresh UI and validate deletion"):

            home.driver.refresh()

            home.wait_for_dom_ready()

            assert not home.is_note_in_ui(title)


    @allure.story("Check Count After Delete")
    @allure.severity(allure.severity_level.NORMAL)
    def test_note_count_after_delete(self, logged_in_driver):

        title = f"Count {int(time.time())}"

        home = ProductPage(logged_in_driver)

        with allure.step("Create note in UI"):

            home.create_note(
                category="Home",
                title=title,
                description="Count test"
            )

        with allure.step("Capture note count before delete"):

            count_before = home.get_note_count()

        api = NotesAPIClient()

        with allure.step("Login using API"):

            api.login(
                UserEmail,
                UserPassword
            )

        with allure.step("Delete note using API"):

            response = api.get_notes()

            note = api.find_note_in_list(
                response,
                title
            )

            assert note is not None

            api.delete_note(note["id"])

        with allure.step("Refresh UI and validate count"):

            home.driver.refresh()

            home.wait_for_dom_ready()

            count_after = home.get_note_count()

            allure.attach(
                f"Before Delete: {count_before}\nAfter Delete: {count_after}",
                name="note_count",
                attachment_type=allure.attachment_type.TEXT
            )

            assert count_after < count_before


    @allure.story("Deleted Note Not In API")
    @allure.severity(allure.severity_level.NORMAL)
    def test_deleted_note_not_in_api(self, logged_in_driver):

        title = f"Remove {int(time.time())}"

        home = ProductPage(logged_in_driver)

        with allure.step("Create note in UI"):

            home.create_note(
                category="Home",
                title=title,
                description="Remove test"
            )

        api = NotesAPIClient()

        with allure.step("Login using API"):

            api.login(
                UserEmail,
                UserPassword
            )

        with allure.step("Delete created note"):

            response = api.get_notes()

            note = api.find_note_in_list(
                response,
                title
            )

            assert note is not None

            api.delete_note(note["id"])

        with allure.step("Validate deleted note not present in API"):

            new_response = api.get_notes()

            deleted_note = api.find_note_in_list(
                new_response,
                title
            )

            assert deleted_note is None