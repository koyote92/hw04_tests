from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus as status_code  # Использую согласно допзаданию.

from ..models import Post, Group

User = get_user_model()

# Не знаю, насколько правильно я делаю, используя одного автора с тестовыми
# постом и группой в setUpClass, а второго в setUp. Но для тестов в любом
# случае нужны были двое.


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_author = User.objects.create_user(
            username='test',
            email='test@example.com',
        )
        cls.authorized_author = Client()
        cls.authorized_author.force_login(cls.test_author)
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.test_post = Post.objects.create(
            id=1,
            text='Тестовый текст',
            author=cls.test_author,
            group=cls.test_group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_public_pages_url_exists_at_desired_location(self):
        """Проверка доступа к общедоступным страницам."""
        public_pages_urls = (
            '/',
            '/group/test-slug/',
            '/profile/test-user/',
            '/posts/1/',
        )
        for value in public_pages_urls:
            response = self.guest_client.get(value)
            with self.subTest(value=value):
                self.assertEqual(response.status_code, status_code.OK)

    def test_public_pages_url_uses_correct_template(self):
        """Проверка шаблонов для общедоступных адресов."""
        public_pages_templates = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/test-user/': 'posts/profile.html',
            '/posts/1/': 'posts/post_details.html',
        }
        for value, expected in public_pages_templates.items():
            response = self.guest_client.get(value)
            with self.subTest(value=value):
                self.assertTemplateUsed(
                    response, expected)

    def test_authorized_pages_url_exists_at_desired_location(self):
        """Проверка доступа к страницам с использованием авторизации
        (все пользователи)."""
        authorized_pages_urls = ('/create/',)
        for item in authorized_pages_urls:
            response = self.authorized_client.get(item)
            with self.subTest(item=item):
                self.assertEqual(response.status_code, status_code.OK)

    def test_authorized_pages_url_uses_correct_template(self):
        """Проверка шаблонов страниц с использованием авторизации
        (все пользователи)."""
        authorized_pages_templates = {
            '/create/': 'posts/create_post.html',
        }
        for value, expected in authorized_pages_templates.items():
            response = self.authorized_client.get(value)
            with self.subTest(value=value):
                self.assertTemplateUsed(response, expected)

    def test_authorized_pages_url_redirects_unauthorized(self):
        """Проверка редиректов неавторизованных пользователей со страниц,
        доступных только авторизованным пользователям."""
        auth_pages_urls_redirects_unauthorized = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
            '/posts/1/delete/': '/auth/login/?next=/posts/1/delete/',
        }
        for value, expected in auth_pages_urls_redirects_unauthorized.items():
            response = self.guest_client.get(value)
            with self.subTest(value=value):
                self.assertRedirects(response, expected)

    def test_author_pages_url_exists_at_desired_location(self):
        """Проверка доступа к страницам с использованием авторизации (страницы
        автора)."""
        author = PostsURLTests.authorized_author
        author_pages_urls = {
            '/posts/1/edit/': '/posts/create_post.html/',
        }
        for value, expected in author_pages_urls.items():
            response = author.get(value)
            with self.subTest(value=value):
                self.assertEqual(response.status_code, status_code.OK)

    def test_author_pages_url_uses_correct_template(self):
        """Проверка шаблонов страниц с использованием авторизации (страницы
        автора)."""
        author = PostsURLTests.authorized_author
        author_pages_templates = {
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for value, expected in author_pages_templates.items():
            response = author.get(value)
            with self.subTest(value=value):
                self.assertTemplateUsed(response, expected)

    def test_authorized_non_author_redirects_on_only_author_actions(self):
        """Проверка редиректа, когда авторизованный пользователь пытается
        редактировать или удалить чужую публикацию."""
        author_only_urls = {
            '/posts/1/edit/': '/posts/1/',
            '/posts/1/delete/': '/posts/1/',
        }
        for value, expected in author_only_urls.items():
            response = self.authorized_client.get(value)
            with self.subTest(value=value):
                self.assertRedirects(response, expected)
