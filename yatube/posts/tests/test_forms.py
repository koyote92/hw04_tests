from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Post, Group

User = get_user_model()


class PostFormTests(TestCase):
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

    def test_create_post(self):
        authorized_client = PostFormTests.authorized_client
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст формы',
            'group__title': 'Тестовая группа',
        }
        authorized_client.post(reverse('posts:post_create'), data=form_data)
        self.assertEqual(posts_count + 1, Post.objects.count())
        self.assertTrue(Post.objects.filter(
            text='Тестовый текст',
            group__title='Тестовая группа',
        ).exists()
                        )

    def test_clean_text(self):
        authorized_client = PostFormTests.authorized_client
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тест',
        }
        response = authorized_client.post(reverse('posts:post_create'),
                                          data=form_data)
        self.assertEqual(posts_count, Post.objects.count())
        self.assertFormError(
            response,
            'form',
            'text',
            'Текст публикации не может быть короче 10 символов.'
        )

    def test_edit_post(self):
        authorized_client = PostFormTests.authorized_client
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Изменённый текст',
        }
        authorized_client.post(
            reverse('posts:post_update', args=str(self.test_post.id)),
            data=form_data,
        )
        self.assertEqual(posts_count, Post.objects.count())
        self.assertTrue(
            Post.objects.filter(
                text='Изменённый текст',
            ).exists()
        )
