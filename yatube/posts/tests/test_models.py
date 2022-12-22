from django.contrib.auth import get_user_model
from django.test import TestCase

from .. import settings
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.test_group = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.test_post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост и ещё несколько лишних символов для теста',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем __str__ у моделей Post и Group."""
        post = PostModelTest.test_post
        group = PostModelTest.test_group
        models_title = {
            str(post): post.text[:settings.SELF_TEXT_LENGTH],
            str(group): group.title
        }
        for title, expected in models_title.items():
            with self.subTest():
                self.assertEqual(title, expected)

    def test_post_verbose_names(self):
        """verbose_name в полях модели post совпадает с ожидаемым."""
        post = PostModelTest.test_post
        field_verbose_names = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_group_verbose_names(self):
        """verbose_name в полях модели group совпадает с ожидаемым."""
        group = PostModelTest.test_group
        field_verbose_names = {
            'title': 'Группа',
            'slug': 'Короткий адрес',
            'description': 'Описание',
        }
        for value, expected in field_verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_post_help_texts(self):
        """help_text в полях модели post совпадает с ожидаемым."""
        post = PostModelTest.test_post
        field_help_texts = {
            'text': 'Текстовое содержимое публикации',
            'pub_date': 'Дата публикации поста',
            'author': 'Имя создателя публикации',
            'group': 'Имя группы для публикаций',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_group_help_texts(self):
        """help_text в полях модели group совпадает с ожидаемым."""
        group = PostModelTest.test_group
        field_help_texts = {
            'title': 'Название группы',
            'slug': 'Короткий идентификатор группы',
            'description': 'Текстовое описание группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)
