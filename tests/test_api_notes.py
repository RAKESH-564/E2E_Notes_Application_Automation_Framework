
import time
import pytest
import allure

from api_client.notes_client import NotesAPIClient


@allure.feature("API - Notes")
@pytest.mark.api
class TestAPIGetNotes:


    @allure.story("Get Notes - Status Code")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_notes_status_200(self, api_client):

        with allure.step("Send GET /notes request"):

            response = api_client.get_notes()

        with allure.step("Validate status code is 200"):

            allure.attach(
                str(response.status_code),
                name="status_code",
                attachment_type=allure.attachment_type.TEXT
            )

            assert response.status_code == 200, \
                f"Expected 200 but got {response.status_code}"


    @allure.story("Get Notes - Response Structure")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_notes_response_structure(self, api_client):

        with allure.step("Send GET /notes request"):

            response = api_client.get_notes()

            body = response.json()

        with allure.step("Validate response contains data list"):

            allure.attach(
                str(body),
                name="response_body",
                attachment_type=allure.attachment_type.JSON
            )

            assert "data" in body, \
                "'data' key missing in response"

            assert isinstance(body["data"], list), \
                "'data' is not a list"


    @allure.story("Get Notes - Response Time")
    @allure.severity(allure.severity_level.MINOR)
    def test_get_notes_response_time(self, api_client):

        with allure.step("Measure GET /notes response time"):

            start = time.time()

            response = api_client.get_notes()

            end = time.time()

            total_time = end - start

        allure.attach(
            str(total_time),
            name="response_time",
            attachment_type=allure.attachment_type.TEXT
        )

        with allure.step("Validate response time"):

            assert response.status_code == 200

            assert total_time <= 2, \
                f"API too slow. Time taken: {total_time}"


@allure.feature("API - Notes")
@pytest.mark.api
class TestAPICreateNote:


    @allure.story("Create Note")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_note_returns_201(self, api_client):

        title = f"API Note {int(time.time())}"

        with allure.step("Create note using API"):

            response = api_client.create_note(
                title=title,
                description="Created using API test",
                category="Home"
            )

        with allure.step("Validate note created successfully"):

            allure.attach(
                response.text,
                name="create_note_response",
                attachment_type=allure.attachment_type.JSON
            )

            assert response.status_code in [200, 201], \
                f"Expected 200 or 201 but got {response.status_code}"


    @allure.story("Create Note - Verify Data")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_note_data_matches(self, api_client):

        title = f"Title Match {int(time.time())}"

        description = "Checking response data"

        with allure.step("Create note using API"):

            response = api_client.create_note(
                title=title,
                description=description,
                category="Work"
            )

            body = response.json()

            data = body.get("data", {})

        with allure.step("Validate note data"):

            allure.attach(
                str(data),
                name="note_data",
                attachment_type=allure.attachment_type.JSON
            )

            assert data.get("title") == title, \
                "Title mismatch"

            assert data.get("description") == description, \
                "Description mismatch"

            assert "id" in data, \
                "Id missing in response"


    @allure.story("Create Note - Verify In Notes List")
    @allure.severity(allure.severity_level.NORMAL)
    def test_created_note_visible_in_get_notes(self, api_client):

        title = f"List Check {int(time.time())}"

        with allure.step("Create note using API"):

            api_client.create_note(
                title=title,
                description="Check note in list",
                category="Personal"
            )

        with allure.step("Fetch notes list"):

            response = api_client.get_notes()

        with allure.step("Validate created note exists in notes list"):

            note = api_client.find_note_in_list(
                response,
                title
            )

            assert note is not None, \
                f"Note '{title}' not found in notes list"


    @allure.story("Create Note - Empty Title")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_create_note_empty_title(self, api_client):

        with allure.step("Send invalid create note request"):

            response = api_client.create_note(
                title="",
                description="No title",
                category="Home"
            )

        with allure.step("Validate validation error"):

            assert response.status_code in [400, 422], \
                f"Expected 400 or 422 but got {response.status_code}"


    @allure.story("Create Note Without Login")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_create_note_without_auth(self):

        client = NotesAPIClient()

        with allure.step("Create note without authentication"):

            response = client.create_note(
                title="Unauthorized",
                description="Should fail"
            )

        with allure.step("Validate unauthorized response"):

            assert response.status_code == 401, \
                f"Expected 401 but got {response.status_code}"


@allure.feature("API - Notes")
@pytest.mark.api
class TestAPIDeleteNote:


    @allure.story("Delete Note")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_note_success(self, api_client):

        title = f"Delete Note {int(time.time())}"

        with allure.step("Create note before delete"):

            create_response = api_client.create_note(
                title=title,
                description="Will be deleted"
            )

            body = create_response.json()

            note_id = body["data"]["id"]

        with allure.step("Delete created note"):

            delete_response = api_client.delete_note(note_id)

        with allure.step("Validate delete response"):

            assert delete_response.status_code in [200, 204], \
                f"Expected 200 or 204 but got {delete_response.status_code}"


    @allure.story("Deleted Note Not In List")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_deleted_note_not_present(self, api_client):

        title = f"Delete Check {int(time.time())}"

        with allure.step("Create note before delete"):

            create_response = api_client.create_note(
                title=title,
                description="Delete verification"
            )

            note_id = create_response.json()["data"]["id"]

        with allure.step("Delete created note"):

            api_client.delete_note(note_id)

        with allure.step("Fetch updated notes list"):

            response = api_client.get_notes()

        with allure.step("Validate deleted note not present"):

            note = api_client.find_note_in_list(
                response,
                title
            )

            assert note is None, \
                f"Deleted note '{title}' still present"


    @allure.story("Delete Invalid Note")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_delete_invalid_note(self, api_client):

        with allure.step("Delete invalid note id"):

            response = api_client.delete_note(
                "000000000000000000000000"
            )

        with allure.step("Validate error response"):

            assert response.status_code in [400, 404], \
                f"Expected 400 or 404 but got {response.status_code}"