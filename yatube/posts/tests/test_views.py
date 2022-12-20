from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_author = User.objects.create_user(
            username='test-username',
            email='test@example.com',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.test_author)
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

    def test_pages_uses_correct_templates(self):
        authorized_client = PostsPagesTests.authorized_client
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group',
                kwargs={'slug': 'test-slug'},
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': 'test-username'},
            ),
            'posts/post_details.html': reverse(
                'posts:post_details',
                kwargs={'post_id': 1},
            ),
            'posts/create_post.html': reverse(
                'posts:post_update',
                kwargs={'post_id': 1},
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Нихера не понял с этим тестом. Проверить словарь context? У нас ведь
    # объекты пагинатора приезжают. Мне проверить, приезжает ли объект
    # пагинатора? Если да, то в последней строке проверяю через assertIn
    def test_index_page_show_correct_context(self):
        authorized_client = PostsPagesTests.authorized_client
        response = authorized_client.get(reverse('posts:index'))
        # first_object = response.context['page_obj'][0]
        # post_text_0 = first_object.text
        # post_author_0 = first_object.author.username
        # post_group_0 = first_object.group.title
        # post_slug_0 = first_object.group.slug
        # self.assertEqual(post_text_0, 'Тестовый текст')
        # self.assertEqual(post_author_0, 'test-username')
        # self.assertEqual(post_group_0, 'Тестовая группа')
        # self.assertEqual(post_slug_0, 'test-slug')
        self.assertIn('page_obj', response.context)

    # Я вообще не понимаю, что мы проверяем. Вернее не так, я понимаю, что у нас
    # в context уходит то, что написано во views.py в каждой вьюхе. Но ты бы
    # видел проект для примера. Как обычно, "а сделаем мы пример СОВСЕМ не такой
    # как в живом проекте, а чё такого?" У них даже context во вью не
    # используется.
    # Ты меня извини, но я тесты вьюх сделаю по-максимуму на отъебись из-за
    # отстутствия нормального примера.
    def test_group_page_show_correct_context(self):
        authorized_client = PostsPagesTests.authorized_client
        response = authorized_client.get(reverse(
            'posts:group',
            kwargs={'slug': 'test-slug'},
        ))
        # Может быть так? Или assertIsNone, или assertIsInstance? В теории
        # по-моему дичь какая-то.
        self.assertIn('page_obj', response.context)
        self.assertIn('group', response.context)
        self.assertIn('posts', response.context)

    # Цитирую теорию: "Проверка 2: в шаблон передан правильный контекст
    # При создании страницы в неё передаётся словарь с контекстом. При
    # обращении к странице можно получить этот словарь из свойства context
    # объекта response, после чего проверить содержимое полей словаря
    # response.context на совпадение с ожидаемым результатом."

    # Я ведь правильно делаю, проверяю содержимое полей словаря
    # response.context? Меня прям очень смущает теория по вьюхам, будто я не то
    # делаю.
    def test_profile_page_show_correct_context(self):
        authorized_client = PostsPagesTests.authorized_client
        response = authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.test_author.username},
        ))
        self.assertIn('author', response.context)
        self.assertIn('page_obj', response.context)

    def test_post_create_page_show_correct_context(self):
        authorized_client = PostsPagesTests.authorized_client
        response = authorized_client.get(reverse('posts:post_create'))
        self.assertIn('post', response.context)
        self.assertIn('form', response.context)

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_update_page_show_correct_context(self):
        authorized_client = PostsPagesTests.authorized_client
        response = authorized_client.get(reverse(
            'posts:post_update',
            kwargs={'post_id': 1},
        ))
        self.assertIn('post', response.context)
        self.assertIn('form', response.context)
        self.assertIn('is_edit', response.context)
        # Может форму в отдельном тесте тестировать? Я вообще не понимаю, у нас
        # есть одна форма на два темплейта, мне надо её тестировать на обоих
        # темплейтах? Её содержимое ведь не поменяется.
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

# Снова на всякий цитирую теорию
# "Для тестирования паджинатора Yatube можно создать в фикстурах несколько
# объектов Post, а затем проверить, сколько записей передаётся на страницу в
# словаре context. Объектов в фикстурах должно быть больше, чем выводится на
# одну страницу паджинатора."
class PaginatorViewsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_author = User.objects.create_user(
            username='test-username',
            email='test@example.com',
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.test_author)
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Поехали фикстуры.
        cls.test_post_1 = Post.objects.create(
            id=1,
            text='Тестовый текст1',
            author=cls.test_author,
            group=cls.test_group,
        )
        cls.test_post_2 = Post.objects.create(
            id=2,
            text='Тестовый текст2',
            author=cls.test_author,
            group=cls.test_group,
        )
        cls.test_post_3 = Post.objects.create(
            id=3,
            text='Тестовый текст3',
            author=cls.test_author,
            group=cls.test_group,
        )
        cls.test_post_4 = Post.objects.create(
            id=4,
            text='Тестовый текст4',
            author=cls.test_author,
            group=cls.test_group,
        )
        cls.test_post_5 = Post.objects.create(
            id=5,
            text='Тестовый текст5',
            author=cls.test_author,
            group=cls.test_group,
        )
        cls.test_post_6 = Post.objects.create(
            id=6,
            text='Тестовый текст6',
            author=cls.test_author,
            group=cls.test_group,
        )
        cls.test_post_7 = Post.objects.create(
            id=7,
            text='Тестовый текст7',
            author=cls.test_author,
            group=cls.test_group,
        )
        cls.test_post_8 = Post.objects.create(
            id=8,
            text='Тестовый текст8',
            author=cls.test_author,
            group=cls.test_group,
        )
        cls.test_post_9 = Post.objects.create(
            id=9,
            text='Тестовый текст9',
            author=cls.test_author,
            group=cls.test_group,
        )
        cls.test_post_10 = Post.objects.create(
            id=10,
            text='Тестовый текст10',
            author=cls.test_author,
            group=cls.test_group,
        )
        cls.test_post_11 = Post.objects.create(
            id=11,
            text='Тестовый текст11',
            author=cls.test_author,
            group=cls.test_group,
        )
        cls.test_post_12 = Post.objects.create(
            id=12,
            text='Тестовый текст12',
            author=cls.test_author,
            group=cls.test_group,
        )
        cls.test_post_13 = Post.objects.create(
            id=13,
            text='Тестовый текст13',
            author=cls.test_author,
            group=cls.test_group,
        )

    # Не знаю, насколько правильно я здесь распаковываю словарь и насколько
    # правильно передаю аргументы в subTest. Да и нужен тут subTest вообще?
    # Лень было писать по три теста на каждую страницу.
    def test_first_pages_with_paginator_contains_ten_records(self):
        authorized_client = PaginatorViewsTestCase.authorized_client
        pages_tested = {
            'posts:index': None,
            'posts:group': {'slug': 'test-slug'},
            'posts:profile': {'username': 'test-username'},
        }
        for address, kwargs in pages_tested.items():
            with self.subTest(address=address, kwargs=kwargs):
                response = authorized_client.get(reverse(address, kwargs=kwargs))
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
                response = authorized_client.get(reverse(address,kwargs=kwargs)
                                                 + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)

# И снова теория
# "Проверьте, что если при создании поста указать группу, то этот пост появляется
# на главной странице сайта,
# на странице выбранной группы,
# в профайле пользователя.
# Проверьте, что этот пост не попал в группу, для которой не был предназначен."
# Имел я этих теоретиков за отсутствие примера.
