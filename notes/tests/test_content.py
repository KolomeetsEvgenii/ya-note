from notes.forms import NoteForm
from notes.tests.auth import BaseNoteTestCase
from notes.tests.urls import ADD_URL, LIST_URL, note_url


class TestContent(BaseNoteTestCase):
    def test_note_in_object_list(self):
        response = self.author_client.get(LIST_URL)
        object_list = response.context['object_list']

        note_from_list = object_list.get(pk=self.note.pk)

        self.assertEqual(note_from_list.title, self.note.title)
        self.assertEqual(note_from_list.text, self.note.text)
        self.assertEqual(note_from_list.slug, self.note.slug)
        self.assertEqual(note_from_list.author, self.note.author)

    def test_user_sees_only_own_notes(self):
        response = self.author_client.get(LIST_URL)
        object_list = response.context['object_list']

        self.assertIn(self.note, object_list)
        self.assertNotIn(self.reader_note, object_list)

    def test_pages_have_note_form(self):
        response = self.author_client.get(ADD_URL)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

        edit_url = note_url('notes:edit', self.note.slug)
        response = self.author_client.get(edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
