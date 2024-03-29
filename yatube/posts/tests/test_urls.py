from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus

from ..models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Я так и не понял, как избавиться от юзера-заглушки здесь, ведь у
        # Post always must be a Lich Ki... author то есть.
        cls.test_author = User.objects.create_user(
            username='test-author',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.test_author)
        cls.test_post = Post.objects.create(
            text='Тестовый текст',
            group=cls.test_group,
            author=cls.test_author,
        )
        # Алексей Григорьев: "урлы с pk поста определять через f-строки"
        cls.url_index = '/'
        cls.url_group = '/group/test-slug/'
        cls.url_profile = '/profile/test-user/'
        cls.url_post_details = f'/posts/{cls.test_post.id}/'  # Так что-ли?
        cls.url_post_create = '/create/'
        cls.url_post_update = '/posts/1/edit/'
        cls.url_post_delete = '/posts/1/delete/'

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_pages_url_exists_at_desired_location(self):
        """Проверка доступа к общедоступным страницам."""
        public_pages_urls = (
            self.url_index,
            self.url_group,
            self.url_profile,
            self.url_post_details,
        )
        for value in public_pages_urls:
            response = self.guest_client.get(value)
            with self.subTest(value=value):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_public_pages_url_uses_correct_template(self):
        """Проверка шаблонов для общедоступных адресов."""
        public_pages_templates = {
            self.url_index: 'posts/index.html',
            self.url_group: 'posts/group_list.html',
            self.url_profile: 'posts/profile.html',
            self.url_post_details: 'posts/post_details.html',
        }
        for value, expected in public_pages_templates.items():
            response = self.guest_client.get(value)
            with self.subTest(value=value):
                self.assertTemplateUsed(
                    response, expected)

    def test_authorized_pages_url_exists_at_desired_location(self):
        """Проверка доступа к страницам с использованием авторизации
        (все пользователи)."""
        authorized_pages_urls = (self.url_post_create,)
        for item in authorized_pages_urls:
            response = self.authorized_client.get(item)
            with self.subTest(item=item):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_pages_url_uses_correct_template(self):
        """Проверка шаблонов страниц с использованием авторизации
        (все пользователи)."""
        authorized_pages_templates = {
            self.url_post_create: 'posts/create_post.html',
        }
        for value, expected in authorized_pages_templates.items():
            response = self.authorized_client.get(value)
            with self.subTest(value=value):
                self.assertTemplateUsed(response, expected)

    def test_authorized_pages_url_redirects_unauthorized(self):
        """Проверка редиректов неавторизованных пользователей со страниц,
        доступных только авторизованным пользователям."""
        auth_pages_urls_redirects_unauthorized = {
            self.url_post_create: '/auth/login/?next=/create/',
            self.url_post_update: '/auth/login/?next=/posts/1/edit/',
            self.url_post_delete: '/auth/login/?next=/posts/1/delete/',
        }
        for value, expected in auth_pages_urls_redirects_unauthorized.items():
            response = self.guest_client.get(value)
            with self.subTest(value=value):
                self.assertRedirects(response, expected)

    def test_author_pages_url_exists_at_desired_location(self):  # Нужен автор.
        """Проверка доступа к страницам с использованием авторизации (страницы
        автора)."""
        test_author = PostsURLTests.authorized_client
        author_pages_urls = {
            self.url_post_update: '/posts/create_post.html/',
        }
        for value, expected in author_pages_urls.items():
            response = test_author.get(value)
            with self.subTest(value=value):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_pages_url_uses_correct_template(self):  # Нужен автор.
        """Проверка шаблонов страниц с использованием авторизации (страницы
        автора)."""
        test_author = PostsURLTests.authorized_client
        author_pages_templates = {
            self.url_post_update: 'posts/create_post.html',
        }
        for value, expected in author_pages_templates.items():
            response = test_author.get(value)
            with self.subTest(value=value):
                self.assertTemplateUsed(response, expected)

    def test_authorized_non_author_redirects_on_only_author_actions(self):
        """Проверка редиректа, когда авторизованный пользователь пытается
        редактировать или удалить чужую публикацию."""
        author_only_urls = {
            self.url_post_update: self.url_post_details,
            self.url_post_delete: self.url_post_details,
        }
        for value, expected in author_only_urls.items():
            response = self.authorized_client.get(value)
            with self.subTest(value=value):
                self.assertRedirects(response, expected)
