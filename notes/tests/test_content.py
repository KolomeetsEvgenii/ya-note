from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()

LIST_URL = reverse('notes:list')


class TestNotesListContainsNotes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.notes = [
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                slug=f'note-{index}',
                author=cls.author,
            )
            for index in range(10)
        ]
        Note.objects.bulk_create(cls.notes)

    def test_note_in_object_list(self):
        self.client.force_login(self.author)
        response = self.client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.notes[0], object_list)


class TestNotePrivate(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author1 = User.objects.create(username='author1')
        cls.author2 = User.objects.create(username='author2')

        cls.note_author1 = Note.objects.create(
            title='Заметка1',
            text='Просто текст.',
            slug='note_author1',
            author=cls.author1,
        )
        cls.note_author2 = Note.objects.create(
            title='Заметка2',
            text='Просто текст.',
            slug='note_author2',
            author=cls.author2,
        )

    def test_user_sees_only_own_notes(self):
        self.client.force_login(self.author1)
        response = self.client.get(LIST_URL)
        object_list = response.context['object_list']
        self.assertIn(self.note_author1, object_list)
        self.assertNotIn(self.note_author2, object_list)

    def test_pages_have_note_form(self):
        self.client.force_login(self.author1)

        response = self.client.get(reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
        response = self.client.get(
            reverse('notes:edit',
                    args=(self.note_author1.slug,))
        )
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
