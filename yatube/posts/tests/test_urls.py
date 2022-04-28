from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTest(
    TestCase
):
    @classmethod
    def setUpClass(
        cls
    ):
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='auth'
        )
        cls.user_auth = User.objects.create_user(
            username='user_auth'
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(
            self.user
        )

    def test_url_exists_at_desired_location(
        self
    ):
        """Общедоступные страницы доступны любому пользователю."""

        url_names = [
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.pk}/',
        ]

        for url in url_names:
            with self.subTest(
                url=url
            ):
                response = self.client.get(
                    url
                )
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

    def test_page_response_an_error(
        self
    ):
        """Страница /unexisting_page/ возвращает ошибку."""

        response = self.client.get(
            '/unexisting_page/'
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND
        )

    def test_create_and_follow_url_exists_at_desired_location(
        self
    ):
        """Страницы /create/ и /follow/
        доступна авторизованному пользователю.
        """

        url_names = [
            '/create/',
            '/follow/',
        ]

        for url in url_names:
            with self.subTest(
                url=url
            ):
                response = self.authorized_client.get(
                    url
                )
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK
                )

    def test_follow_url_exists_at_desired_location(
        self
    ):
        """Страницы profile/<str:username>/follow/
        и profile/<str:username>/follow/
        доступны авторизованному пользователю.
        """

        url_names = [
            f'/profile/{self.user.username}/follow/',
            f'/profile/{self.user.username}/unfollow/',
            f'/posts/{self.post.pk}/comment/'
        ]

        for url in url_names:
            with self.subTest(
                url=url
            ):
                response = self.authorized_client.get(
                    url
                )
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.FOUND
                )

    def test_create_url_redirect_anonymous(
        self
    ):
        """Страница /create/ перенаправляет анонимного пользователя."""

        response = self.client.get(
            '/create/',
            follow=True
        )
        self.assertRedirects(
            response,
            '/auth/login/?next=/create/'
        )

    def test_post_edit_url_exists_at_desired_location(
        self
    ):
        """Страница /posts/<int:post_id>/edit/ доступна автору."""

        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/edit/'
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK
        )

    def test_post_edit_url_redirect_anonymous(
        self
    ):
        """Страница /posts/<int:post_id>/edit/
        перенаправляет анонимного пользователя.
        """

        response = self.client.get(
            f'/posts/{self.post.pk}/edit/',
            follow=True
        )
        self.assertRedirects(
            response,
            '/auth/login/?next=/posts/1/edit/'
        )

    def test_urls_uses_correct_template(
        self
    ):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(
                address=address
            ):
                response = self.authorized_client.get(
                    address
                )
                self.assertTemplateUsed(
                    response,
                    template
                )
