from http import HTTPStatus

from notes.models import Note
from notes.tests.auth import BaseNoteTestCase
from notes.tests.urls import (
    ADD_URL,
    HOME_URL,
    LIST_URL,
    LOGIN_URL,
    LOGOUT_URL,
    SIGNUP_URL,
    SUCCESS_URL,
    note_url,
)


class TestRoutes(BaseNoteTestCase):
    def test_pages_availability_for_users(self):
        public_pages = (HOME_URL, LOGIN_URL, SIGNUP_URL)
        for url in public_pages:
            with self.subTest(user='anonymous', url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

        common_pages = (ADD_URL, LIST_URL, SUCCESS_URL)
        for client_name, client in (
            ('author', self.author_client),
            ('reader', self.reader_client),
        ):
            for url in common_pages:
                with self.subTest(user=client_name, url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

        note_pages = (
            note_url('notes:edit', self.note.slug),
            note_url('notes:detail', self.note.slug),
            note_url('notes:delete', self.note.slug),
        )
        for url in note_pages:
            with self.subTest(user='author', url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

            with self.subTest(user='reader', url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirects_for_anonymous_user(self):
        protected_pages = (
            ADD_URL,
            LIST_URL,
            SUCCESS_URL,
            note_url('notes:edit', self.note.slug),
            note_url('notes:detail', self.note.slug),
            note_url('notes:delete', self.note.slug),
        )
        for url in protected_pages:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, f'{LOGIN_URL}?next={url}')

        with self.subTest(url=LOGOUT_URL):
            notes_before = Note.objects.count()
            response = self.client.post(LOGOUT_URL)
            self.assertIn(
                response.status_code,
                (HTTPStatus.OK, HTTPStatus.FOUND)
            )
            self.assertEqual(Note.objects.count(), notes_before)
