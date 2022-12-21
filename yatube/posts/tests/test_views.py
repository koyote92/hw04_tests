from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()

# А ты имеешь доступ к теории яндекса вообще, смотрел её? В моделях и урлах
# всё понятно, доходим до вьюх и БАХ! Всё, как будто составителя теории сменили


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Снова ситуация, если не буду создавать тестового юзера (автора)
        # здесь, то база скажет "NOT NULL constraint failed." Тестовый пост в
        # setUp или оставить здесь вместе с юзером-заглушкой? Проверять всё
        # равно всё буду юзером из setUp.
        cls.test_user = User.objects.create_user(
            username='test-username'
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.test_user)
        cls.test_post = Post.objects.create(
            text='Тестовый текст',
            author=cls.test_user,
            group=cls.test_group,
        )

        cls.url_index = reverse('posts:index')
        cls.url_group = reverse(
            'posts:group',
            kwargs={'slug': 'test-slug'},
        )
        cls.url_profile = reverse(
            'posts:profile',
            kwargs={'username': 'test-username'},
        )
        cls.url_post_details = reverse(
            'posts:post_details',
            kwargs={'post_id': 1},
        )
        cls.url_post_create = reverse('posts:post_create')
        cls.url_post_update = reverse(
            'posts:post_update',
            kwargs={'post_id': 1},
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_templates(self):  # Здесь нужен юзер-автор.
        authorized_client = PostsPagesTests.authorized_client
        templates_pages_names = {
            self.url_index: 'posts/index.html',
            self.url_group: 'posts/group_list.html',
            self.url_profile: 'posts/profile.html',
            self.url_post_details: 'posts/post_details.html',
            self.url_post_create: 'posts/create_post.html',  # Тупанул с key.
            self.url_post_update: 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(self.url_index)
        self.assertIn('page_obj', response.context)

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(self.url_group)
        self.assertIn('page_obj', response.context)
        self.assertIn('group', response.context)
        self.assertIn('posts', response.context)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(self.url_profile)
        self.assertIn('author', response.context)
        self.assertIn('page_obj', response.context)

    def test_post_create_page_show_correct_context(self):
        response = self.authorized_client.get(self.url_post_create)
        self.assertIn('post', response.context)
        self.assertIn('form', response.context)

    def test_post_update_page_show_correct_context(self):  # Здесь тоже.
        authorized_client = PostsPagesTests.authorized_client
        response = authorized_client.get(self.url_post_update)
        self.assertIn('post', response.context)
        self.assertIn('form', response.context)
        self.assertIn('is_edit', response.context)

    def test_created_post_shows_on_different_urls(self):
        different_urls = (self.url_index, self.url_group, self.url_profile)
        for item in different_urls:
            with self.subTest(item=item):
                response = self.guest_client.get(item)
                self.assertEqual(
                    response.context['page_obj'][0].text,
                    'Тестовый текст',
                )
                self.assertEqual(
                    response.context['page_obj'][0].author.username,
                    'test-username',
                )
                self.assertEqual(
                    response.context['page_obj'][0].group.title,
                    'Тестовая группа',
                )
    # Тут я не понимаю, почему у меня с nested dictionary вот эта строка
    # райзит TypeError, поэтому указываю через [0]
    # self.assertEqual(response.context['page_obj']['object_list'].text,
    # 'Тестовый текст')


class PaginatorViewsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_author = User.objects.create_user(
            username='test-username',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.test_author)
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Поехали фикстуры.
        # А зачем тут bulk_create?
        # [Post.objects.create(
        #     text='Тестовый текст ' + str(i),
        #     author=cls.test_author,
        #     group=cls.test_group)
        #     for i in range(13)]
        # Ну или так.
        fixtures = [Post(
            text='Тестовый текст' + str(i),
            author=cls.test_author,
            group=cls.test_group)
            for i in range(13)]
        Post.objects.bulk_create(fixtures)

    def test_first_pages_with_paginator_contains_ten_records(self):
        authorized_client = PaginatorViewsTestCase.authorized_client
        pages_tested = {
            'posts:index': None,
            'posts:group': {'slug': 'test-slug'},
            'posts:profile': {'username': 'test-username'},
        }
        for address, kwargs in pages_tested.items():
            with self.subTest(address=address, kwargs=kwargs):
                response = authorized_client.get(reverse(
                    address,
                    kwargs=kwargs
                ))
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_pages_with_paginator_contains_three_records(self):
        authorized_client = PaginatorViewsTestCase.authorized_client
        pages_tested = {
            'posts:index': None,
            'posts:group': {'slug': 'test-slug'},
            'posts:profile': {'username': 'test-username'},
        }
        for address, kwargs in pages_tested.items():
            with self.subTest(address=address, kwargs=kwargs):
                response = authorized_client.get(reverse(
                    address,
                    kwargs=kwargs
                ) + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
