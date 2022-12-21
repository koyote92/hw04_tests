from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from http import HTTPStatus as status_code

from ..forms import PostForm
from ..models import Post, Group

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
        )
        cls.url_post_create = reverse('posts:post_create')
        cls.url_post_update = reverse(
            'posts:post_update',
            kwargs={'post_id': 1},
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        form_data = {
            'text': 'Тестовый текст формы',
            # 'group': self.test_group  # Тут я застрял. Без группы создаётся,
            # с группой нет. Вживую всё работает. Не понимаю почему.
        }
        response = self.authorized_client.post(self.url_post_create,
                                               data=form_data, follow=True)
        post = Post.objects.get(id=1)
        self.assertEqual(response.status_code, status_code.OK)
        self.assertEqual(1, Post.objects.count())
        self.assertEqual(post.text, 'Тестовый текст формы')
        self.assertEqual(post.author.username, 'test-user')

    def test_clean_text(self):
        form_data = {
            'text': 'Тест',
        }
        response = self.authorized_client.post(
            self.url_post_create,
            data=form_data,
        )
        self.assertEqual(0, Post.objects.count())
        self.assertFormError(
            response,
            'form',
            'text',
            'Текст публикации не может быть короче 10 символов.'
        )

    def test_edit_post(self):
        Post.objects.create(text='Изначальный текст!!!', author=self.user)
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Изменённый текст',
        }
        self.authorized_client.post(self.url_post_update, data=form_data)
        self.assertEqual(posts_count, Post.objects.count())
        self.assertTrue(Post.objects.filter(text='Изменённый текст').exists())
        self.assertEqual(Post.objects.get(id=1).text, 'Изменённый текст')
        # Лучше Equal?
