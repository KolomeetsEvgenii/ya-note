# flake8: noqa
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Авторизированный')
        cls.reader = User.objects.create(username='Аноноимный')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test-slug',
            author=cls.author,
        )

    def test_home_page(self):
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:signup'),
        )

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author_and_reader(self):

        common_urls = (
            'notes:add',
            'notes:list',
            'notes:success',
        )

        for user in (self.author, self.reader):
            self.client.force_login(user)
            for name in common_urls:
                with self.subTest(user=user.username, name=name):
                    url = reverse(name)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )

        note_args = (self.note.slug,)
        urls = (
            ('notes:edit', note_args),
            ('notes:detail', note_args),
            ('notes:delete', note_args),
        )

        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(user=user.username, name=name, args=args):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):

        note_args = (self.note.slug,)
        urls = (
            ('notes:edit', note_args),
            ('notes:detail', note_args),
            ('notes:delete', note_args),
            ('notes:add', ()),
            ('notes:list', ()),
            ('notes:success', ()),
        )

        login_url = reverse('users:login')

        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
