from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING
from pytils.translit import slugify

User = get_user_model()


class TestNoteCreation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='User')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': 'New note',
            'text': 'Text of note',
            'slug': 'text-of-slug'
        }

    def test_auth_user_can_create_note(self):
        notes_before = Note.objects.count()

        response = self.auth_client.post(self.url, data=self.form_data)

        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), notes_before + 1)

        note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.user)

    def test_anonymous_cant_create_note(self):
        notes_before = Note.objects.count()

        response = self.client.post(self.url, data=self.form_data)

        self.assertEqual(Note.objects.count(), notes_before)
        login_url = reverse('users:login')
        self.assertRedirects(response, f'{login_url}?next={self.url}')

    def test_cant_create_two_notes_with_same_slug(self):
        notes_before = Note.objects.count()

        response1 = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response1, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), notes_before + 1)

        response2 = self.auth_client.post(self.url, data=self.form_data)
        self.assertEqual(response2.status_code, HTTPStatus.OK)
        self.assertEqual(Note.objects.count(), notes_before + 1)

        form = response2.context['form']
        self.assertIn('slug', form.errors)
        self.assertIn(WARNING, form.errors['slug'][0])

    def test_auto_slug(self):
        title = 'Auto slug note'
        notes_before = Note.objects.count()

        response = self.auth_client.post(
            self.url,
            data={'title': title, 'text': 'Text of note', 'slug': ''}
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), notes_before + 1)

        note = Note.objects.get(title=title, author=self.user)
        self.assertEqual(note.slug, slugify(title)[:100])


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённая заметка'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='title',
            author=cls.author,
            text=cls.NOTE_TEXT,
            slug='note-slug',
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.note.title,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.note.slug,
        }

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
