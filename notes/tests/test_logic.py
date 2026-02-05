from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.auth import BaseNoteTestCase
from notes.tests.urls import ADD_URL, LOGIN_URL, SUCCESS_URL, note_url


class TestNoteCreation(BaseNoteTestCase):
    def test_auth_user_can_create_note(self):
        form_data = {
            'title': 'New note',
            'text': 'Text of note',
            'slug': 'text-of-slug',
        }
        notes_before = Note.objects.count()

        response = self.author_client.post(ADD_URL, data=form_data)

        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_before + 1)

        note = Note.objects.get(slug=form_data['slug'])
        self.assertEqual(note.title, form_data['title'])
        self.assertEqual(note.text, form_data['text'])
        self.assertEqual(note.slug, form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_cant_create_note(self):
        form_data = {
            'title': 'New note',
            'text': 'Text of note',
            'slug': 'text-of-slug',
        }
        notes_before = Note.objects.count()

        response = self.client.post(ADD_URL, data=form_data)

        self.assertEqual(Note.objects.count(), notes_before)
        self.assertRedirects(response, f'{LOGIN_URL}?next={ADD_URL}')

    def test_cant_create_two_notes_with_same_slug(self):
        form_data = {
            'title': 'New note',
            'text': 'Text of note',
            'slug': 'text-of-slug',
        }
        notes_before = Note.objects.count()

        response1 = self.author_client.post(ADD_URL, data=form_data)
        self.assertRedirects(response1, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_before + 1)

        response2 = self.author_client.post(ADD_URL, data=form_data)
        self.assertEqual(response2.status_code, HTTPStatus.OK)
        self.assertEqual(Note.objects.count(), notes_before + 1)

        form = response2.context['form']
        self.assertIn('slug', form.errors)
        self.assertIn(WARNING, form.errors['slug'][0])

    def test_auto_slug(self):
        title = 'Auto slug note'
        notes_before = Note.objects.count()

        response = self.author_client.post(
            ADD_URL,
            data={'title': title, 'text': 'Text of note', 'slug': ''},
        )

        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_before + 1)

        note = Note.objects.get(title=title, author=self.author)
        self.assertEqual(note.slug, slugify(title)[:100])


class TestNoteEditDelete(BaseNoteTestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённая заметка'

    def _note_snapshot(self, note_pk: int) -> dict:
        note = Note.objects.get(pk=note_pk)
        return {
            'title': note.title,
            'text': note.text,
            'slug': note.slug,
            'author_id': note.author_id,
        }

    def test_author_can_delete_note(self):
        delete_url = note_url('notes:delete', self.note.slug)
        notes_before = Note.objects.count()

        response = self.author_client.post(delete_url)

        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_before - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_user_cant_delete_note_of_another_user(self):
        delete_url = note_url('notes:delete', self.note.slug)
        notes_before = Note.objects.count()
        before = self._note_snapshot(self.note.pk)

        response = self.reader_client.post(delete_url)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_before)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
        self.assertEqual(self._note_snapshot(self.note.pk), before)

    def test_author_can_edit_note(self):
        edit_url = note_url('notes:edit', self.note.slug)
        notes_before = Note.objects.count()

        form_data = {
            'title': self.note.title,
            'text': self.NEW_NOTE_TEXT,
            'slug': self.note.slug,
        }

        response = self.author_client.post(edit_url, data=form_data)

        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_before)

        updated = Note.objects.get(pk=self.note.pk)
        self.assertEqual(updated.title, form_data['title'])
        self.assertEqual(updated.text, form_data['text'])
        self.assertEqual(updated.slug, form_data['slug'])
        self.assertEqual(updated.author, self.author)

    def test_user_cant_edit_note_of_another_user(self):
        edit_url = note_url('notes:edit', self.note.slug)
        notes_before = Note.objects.count()
        before = self._note_snapshot(self.note.pk)

        form_data = {
            'title': self.note.title,
            'text': self.NEW_NOTE_TEXT,
            'slug': self.note.slug,
        }

        response = self.reader_client.post(edit_url, data=form_data)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_before)
        self.assertEqual(self._note_snapshot(self.note.pk), before)
