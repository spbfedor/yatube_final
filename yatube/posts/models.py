from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models

User = get_user_model()


class Group(
    models.Model
):
    title = models.CharField(
        max_length=200
    )
    slug = models.SlugField(
        max_length=200,
        unique=True
    )
    description = models.TextField()

    def __str__(
        self
    ):
        return self.slug


class Post(
    models.Model
):
    text = models.TextField(
        validators=[
            MinLengthValidator(
                limit_value=15,
                message="Длина этого поля должна быть не менее 15 символов"
            )
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = [
            '-pub_date'
        ]

    def __str__(
        self
    ):
        return self.text


class Comment(
    models.Model
):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            '-created'
        ]

    def __str__(
        self
    ):
        return self.text


class Follow(
    models.Model
):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    def __str__(
        self
    ):
        return self.user.username
