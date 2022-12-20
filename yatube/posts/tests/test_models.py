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
        cls.test_group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.test_group_2 = Group.objects.create(
            title='Ж' * 80,
            description='Тестовое описание',
        )
        cls.test_post_1 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.test_post_2 = Post.objects.create(
            author=cls.user,
            text='Тестовый пост и немного дополнительных символов',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем __str__ у моделей Post и Group."""
        post = PostModelTest.test_post_1
        expected_object_name = post.text[:settings.SELF_TEXT_LENGTH]
        self.assertEqual(expected_object_name, str(post))

        post = PostModelTest.test_post_2
        expected_object_name = post.text[:settings.SELF_TEXT_LENGTH]
        self.assertEqual(expected_object_name, str(post))

        group = PostModelTest.test_group_1
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

        group = PostModelTest.test_group_2
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_post_verbose_names(self):
        """verbose_name в полях модели post совпадает с ожидаемым."""
        post = PostModelTest.test_post_1
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
        group = PostModelTest.test_group_1
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
        post = PostModelTest.test_post_1
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
        group = PostModelTest.test_group_1
        field_help_texts = {
            'title': 'Название группы',
            'slug': 'Короткий идентификатор группы',
            'description': 'Текстовое описание группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    # Тут я баловался))

    # def test_group_title_max_length_not_exceed(self):
    #     """При превышении max_length поля title возникает ValidationError."""
    #     group = PostModelTest.test_group_2
    #     group.title = 'test-title'*20
    #     with self.assertRaises(ValidationError):
    #         group.full_clean()
#
    # def test_description_is_not_empty(self):
    #     """При пустом поле description возникает ValidationError."""
    #     group = PostModelTest.test_group_2
    #     group.description = None
    #     with self.assertRaises(ValidationError):
    #         group.full_clean()
#
    # def test_group_slug_is_unique(self):  # ЭТО БЫЛО СЛОЖНО!
    #     """При создании группы с уже существующим slug возникает
    #     IntegrityError."""
    #     group = Group(
    #         title=PostModelTest.test_group_2.title,
    #         description='1',
    #     )
    #     with self.assertRaises(Exception) as raised:
    #         group.save()
    #     self.assertEqual(IntegrityError, type(raised.exception))
