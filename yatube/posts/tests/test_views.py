import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post
from ..views import NAMBER_OF_POSTS

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPages(TestCase):
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

        cls.user_follower = User.objects.create_user(
            username='follower',
        )
        cls.user_2 = User.objects.create_user(
            username='user',
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
            author=cls.user,
            post=cls.post,
            text='Тестовый комментарий',
        )
        cls.follow = Follow.objects.create(
            user=cls.user_follower,
            author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(
        self
    ):
        self.authorized_client_1 = Client()
        self.authorized_client_1.force_login(
            self.user,
        )
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(
            self.user_follower,
        )
        self.authorized_client_3 = Client()
        self.authorized_client_3.force_login(
            self.user_2,
        )

    def test_pages_uses_correct_template(
        self
    ):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            reverse(
                'app_posts:index'
            ): 'posts/index.html',
            (
                reverse(
                    'app_posts:group_list',
                    kwargs={
                        'slug': self.group.slug
                    }
                )
            ): 'posts/group_list.html',
            (
                reverse(
                    'app_posts:profile',
                    kwargs={
                        'username': self.user.username
                    }
                )
            ): 'posts/profile.html',
            (
                reverse(
                    'app_posts:post_detail',
                    kwargs={
                        'post_id': self.post.pk
                    }
                )
            ): 'posts/post_detail.html',
            (
                reverse(
                    'app_posts:post_edit',
                    kwargs={
                        'post_id': self.post.pk
                    }
                )
            ): 'posts/create_post.html',
            (
                reverse(
                    'app_posts:post_create',
                )
            ): 'posts/create_post.html',
            (
                reverse(
                    'app_posts:follow_index'
                )
            ): 'posts/follow.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(
                reverse_name=reverse_name
            ):
                response = self.authorized_client_1.get(
                    reverse_name
                )
                self.assertTemplateUsed(
                    response, template
                )

    def test_index_and_profile_page_show_correct_context(
        self
    ):
        """Шаблон index и profile сформирован с правильным контекстом."""

        def check(address, object):
            response = self.authorized_client_1.get(
                address
            )
            first_object = response.context[
                object
            ][
                0
            ]
            first_dict = {
                first_object.text: self.post.text,
                first_object.author.username: self.user.username,
                first_object.pk: self.post.pk,
                first_object.group: self.group,
                first_object.title: self.title,
                first_object.description: self.description,
                first_object.slug: self.slug,
                first_object.image: self.small_gif,
                first_object.text: self.comment.text,
            }
            for expected, actual in first_dict.items():
                with self.subTest(
                    expected=expected
                ):
                    self.assertEqual(
                        expected, actual
                    )

            check(
                reverse(
                    'app_posts:index'
                ),
                'page_obj'
            )

            check(
                reverse(
                    'app_posts:profile',
                    kwargs={
                        'username': self.user.username
                    }
                ),
                'page_obj'
            )

            check(
                reverse(
                    'app_posts:post_detail',
                    kwargs={
                        'post_id': self.post.pk
                    }
                ),
                'post_list'
            )
            check(
                reverse(
                    'app_posts:follow_index',
                    kwargs={
                        'username': self.user.username
                    }
                ),
                'page_obj'
            )

    def test_group_list_page_show_correct_context(
        self
    ):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client_1.get(
            reverse(
                'app_posts:group_list',
                kwargs={
                    'slug': self.group.slug
                }
            )
        )
        resp_dict = {
            response.context[
                'group'
            ].title: self.group.title,
            response.context[
                'group'
            ].slug: self.group.slug,
            response.context[
                'group'
            ].description: self.group.description,
            response.context[
                'group'
            ].pk: self.group.pk,
            response.context[
                'page_obj'
            ][0].image: self.post.image
        }
        for expected, actual in resp_dict.items():
            with self.subTest(
                expected=expected
            ):
                self.assertEqual(
                    expected, actual
                )

    def test_post_create_show_correct_context(
        self
    ):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client_1.get(
            reverse(
                'app_posts:post_create'
            )
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(
                value=value
            ):
                form_field = response.context.get(
                    'form'
                ).fields.get(
                    value
                )

                self.assertIsInstance(
                    form_field,
                    expected
                )

    def test_post_edit_show_correct_context(
        self
    ):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client_1.get(
            reverse(
                'app_posts:post_edit',
                kwargs={
                    'post_id': self.post.pk
                }
            )
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(
                value=value
            ):
                form_field = response.context.get(
                    'form'
                ).fields.get(
                    value
                )

                self.assertIsInstance(
                    form_field,
                    expected
                )

    def the_comment_appears_on_the_page_of_the_post(
        self
    ):
        response = self.authorized_client_1.get(
            reverse(
                'app_posts:post_detail',
                kwargs={
                    'post_id': self.post.pk
                }
            )
        )
        self.assertIn(
            self.comment,
            response.context[
                'comments'
            ]
        )

    def test_recording_in_the_feed(
        self
    ):
        """Тестирование ленты подписчика"""
        Follow.objects.create(
            user=self.user_follower,
            author=self.post.author
        )
        response = self.authorized_client_2.get(
            reverse(
                'app_posts:follow_index'
            )
        )
        self.assertIn(
            self.post,
            response.context[
                'page_obj'
            ]
        )

    def test_an_unsigned_user_feed(
        self
    ):
        """Тестирование ленты неподписанного пользователя"""
        response = self.authorized_client_3.get(
            reverse(
                'app_posts:follow_index'
            )
        )
        self.assertNotIn(
            self.post, response.context[
                'page_obj'
            ]
        )

    def test_profile_follow(
        self
    ):
        """Пользователь может подписаться на автора"""
        form_data = {
            'user': self.user_follower,
            'author': self.user,
        }
        self.authorized_client_2.post(
            reverse(
                'app_posts:profile_follow',
                kwargs={
                    'username': self.user.username
                }
            ),
            data=form_data,
            follow=True
        )
        follow = Follow.objects.order_by(
            '-pk'
        )[
            0
        ]
        verification_dict = {
            follow.user: form_data['user'],
            follow.author: form_data['author']
        }

        for actual, expected in verification_dict.items():
            with self.subTest(
                actual=actual
            ):

                self.assertEqual(
                    actual, expected
                )

    def test_profile_unfollow(
        self
    ):
        """Пользователь может отписаться от автора"""

        follow_count = Follow.objects.count()
        form_data = {
            'user': self.user_follower,
            'author': self.user,
        }
        self.authorized_client_2.post(
            reverse(
                'app_posts:profile_unfollow',
                kwargs={
                    'username': self.user.username
                }
            ),
            data=form_data,
            follow=True
        )
        count_follow = Follow.objects.count()
        self.assertEqual(
            follow_count - 1,
            count_follow
        )


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(
        cls
    ):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='auth',
        )

        cls.post = []
        for number in range(13):
            cls.post.append(
                Post(
                    text=f'Тестовый пост номер {number}',
                    author=cls.user
                )
            )
        Post.objects.bulk_create(cls.post)

    def test_first_page_contains_ten_records(
        self
    ):
        response = self.client.get(
            reverse(
                'app_posts:index'
            )
        )

        self.assertEqual(
            len(
                response.context[
                    'page_obj'
                ]
            ),
            NAMBER_OF_POSTS
        )

    def test_second_page_contains_three_records(
        self
    ):
        response = self.client.get(
            reverse(
                'app_posts:index'
            ) + '?page=2'
        )
        self.assertEqual(
            len(
                response.context[
                    'page_obj'
                ]
            ),
            Post.objects.count() - NAMBER_OF_POSTS
        )
