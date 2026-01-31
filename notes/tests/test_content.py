# flake8: noqa
from datetime import datetime, timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()

class TestHomePage(TestCase):
    HOME_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Комментатор')
        cls.notes = Note.objects.bulk_create(
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                slug=f'note-{index}',
                author=cls.author,
            )
            for index in range(10)
    )

    def test_news_count(self):
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        self.assertIn(self.notes[0], object_list)
