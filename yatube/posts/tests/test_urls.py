from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus as status_code  # Использую согласно допзаданию.

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
        # Под "лучше засетапить урлы" я понял это:
        cls.url_index = '/'
        cls.url_group = '/group/test-slug/'
        cls.url_profile = '/profile/test-user/'
        cls.url_post_details = '/posts/1/'
        cls.url_post_create = '/create/'
        cls.url_post_update = '/posts/1/edit/'
        cls.url_post_delete = '/posts/1/delete/'

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.second_user = User.objects.create_user(username='2nd-test-user')
        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(self.second_user)
        # Получается, если поместить создание поста сюда, то пост будет
        # пересоздаваться перед каждым тестом. Учитывая, что нам по сути
        # нужен только один пост, чтобы проверить урлы, то его лучше поместить
        # в setUpClass? Если да, то есть смысл вернуть и одного юзера туда же,
        # ведь я 1) проверяю шаблоны и урлы, которые доступны ТОЛЬКО автору
        # 2) проверяю, редиректит ли другого авторизованного юзера, если он
        # пытается редактировать или удалить чужой пост.
        self.test_post = Post.objects.create(
            text='Тестовый текст',
            group=self.test_group,
            author=self.user,
        )

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
                self.assertEqual(response.status_code, status_code.OK)

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
                self.assertEqual(response.status_code, status_code.OK)

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

    def test_author_pages_url_exists_at_desired_location(self):
        """Проверка доступа к страницам с использованием авторизации (страницы
        автора)."""
        author_pages_urls = {
            self.url_post_update: '/posts/create_post.html/',
        }
        for value, expected in author_pages_urls.items():
            response = self.authorized_client.get(value)
            with self.subTest(value=value):
                self.assertEqual(response.status_code, status_code.OK)

    def test_author_pages_url_uses_correct_template(self):
        """Проверка шаблонов страниц с использованием авторизации (страницы
        автора)."""
        author_pages_templates = {
            self.url_post_update: 'posts/create_post.html',
        }
        for value, expected in author_pages_templates.items():
            response = self.authorized_client.get(value)
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
            response = self.second_authorized_client.get(value)
            with self.subTest(value=value):
                self.assertRedirects(response, expected)
