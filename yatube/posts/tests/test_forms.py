import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostForm(TestCase):
    @classmethod
    def setUpClass(
        cls
    ):
        super().setUpClass()

        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

        cls.user = User.objects.create_user(
            username='auth',
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост 555',
            group=cls.group,
            image=cls.uploaded,
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый коммент'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(
            self.user
        )

    def test_create_post_form(self):
        """Валидная форма создает запись в Post."""

        posts_count = Post.objects.count()
        form_data = {
            'text': self.post.text,
            'group': self.group.pk,
            'image': self.post.image
        }

        response = self.authorized_client.post(
            reverse(
                'app_posts:post_create'
            ),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse(
                'app_posts:profile',
                kwargs={
                    'username': self.user.username
                }
            )
        )

        self.assertEqual(
            Post.objects.count(),
            posts_count + 1
        )

        last_post = Post.objects.order_by('-pk')[0]

        verification_dict = {
            last_post.text: form_data['text'],
            last_post.group.pk: form_data['group']
        }

        for actual, expected in verification_dict.items():
            with self.subTest(
                actual=actual
            ):

                self.assertEqual(
                    actual, expected
                )

    def test_post_edit_existing_slug(
        self
    ):

        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse(
                'app_posts:post_edit',
                args=(
                    self.post.pk,
                )
            ),
            data=form_data,
            follow=True
        )

        self.assertEqual(
            Post.objects.count(),
            posts_count
        )

        self.assertFormError(
            response,
            'form',
            'text',
            'Длина этого поля должна быть не менее 15 символов'
        )

        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )

    def test_for_updatinga_record_in_the_database(self):
        """Форма перезаписывает запись в БД"""

        form_data = {
            'text': self.post.text,
            'group': self.group.pk,
            'image': self.post.image,
        }
        self.authorized_client.post(
            reverse(
                'app_posts:post_edit',
                args=(
                    self.post.pk,
                )
            ),
            data=form_data,
            follow=True
        )

        edited_post = Post.objects.get(pk=self.post.pk)

        verification_dict = {
            edited_post.text: form_data['text'],
            edited_post.group.pk: form_data['group'],
            edited_post.image: form_data['image']
        }

        for actual, expected in verification_dict.items():
            with self.subTest(
                actual=actual
            ):

                self.assertEqual(
                    actual, expected
                )

    def test_create_comment(self):
        """Валидная форма создает запись в Comment."""

        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post.pk,
            'author': self.user,
            'text': self.comment.text
        }

        response = self.authorized_client.post(
            reverse(
                'app_posts:add_comment',
                kwargs={
                    'post_id': self.post.pk,
                }
            ),
            data=form_data,
            follow=True,
        )

        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )
        self.assertEqual(
            Comment.objects.count(),
            comment_count + 1
        )
