import requests

from config.config import (
    BASE_API_URL,
    API_TIMEOUT
)


class NotesAPIClient:

    def __init__(self):

        self.base_url =  BASE_API_URL

        self.session = requests.Session()

        self.session.headers.update({
            "Content-Type": "application/json"
        })

        self.token = None


    # -----------------------------
    # Login
    # -----------------------------

    def login(self, email, password):

        url = f"{self.base_url}/users/login"

        payload = {
            "email": email,
            "password": password
        }

        response = self.session.post(
            url,
            json=payload,
            timeout=API_TIMEOUT
        )

        if response.status_code == 200:

            body = response.json()

            self.token = body["data"]["token"]

            self.session.headers.update({
                "x-auth-token": self.token
            })

        return response


    # -----------------------------
    # Get Notes
    # -----------------------------

    def get_notes(self):

        url = f"{self.base_url}/notes"

        response = self.session.get(
            url,
            timeout=API_TIMEOUT
        )

        return response


    # -----------------------------
    # Create Note
    # -----------------------------

    def create_note(
            self,
            title,
            description,
            category="Home"
    ):

        url = f"{self.base_url}/notes"

        payload = {
            "title": title,
            "description": description,
            "category": category
        }

        response = self.session.post(
            url,
            json=payload,
            timeout=API_TIMEOUT
        )

        return response


    # -----------------------------
    # Delete Note
    # -----------------------------

    def delete_note(self, note_id):

        url = f"{self.base_url}/notes/{note_id}"

        response = self.session.delete(
            url,
            timeout=API_TIMEOUT
        )

        return response


    # -----------------------------
    # Get Note By Id
    # -----------------------------

    def get_note_by_id(self, note_id):

        url = f"{self.base_url}/notes/{note_id}"

        response = self.session.get(
            url,
            timeout=API_TIMEOUT
        )

        return response


    # -----------------------------
    # Update Note
    # -----------------------------

    def update_note(self, note_id, payload):

        url = f"{self.base_url}/notes/{note_id}"

        response = self.session.patch(
            url,
            json=payload,
            timeout=API_TIMEOUT
        )

        return response


    # -----------------------------
    # Find Note In List
    # -----------------------------

    def find_note_in_list(self, response, title):

        body = response.json()

        notes = body.get("data", [])

        for note in notes:

            if note.get("title") == title:

                return note

        return None