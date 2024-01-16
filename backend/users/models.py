from django.db import models
from django.contrib.auth.models import AbstractUser

from core.consts import LENGTH_CHARFIELD, LENGTH_EMAILFIELD
from core.validators import username_validator


class User(AbstractUser):
    email = models.EmailField(
        'Электронная почта',
        max_length=LENGTH_EMAILFIELD,
        unique=True,
        help_text=(
            'Укажите уникальный юзернейм. Может содержать до '
            f'{LENGTH_EMAILFIELD} символов.'
        ),
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=LENGTH_CHARFIELD,
        unique=True,
        validators=(username_validator,),
    )
    first_name = models.CharField(
        'Имя',
        max_length=LENGTH_CHARFIELD,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=LENGTH_CHARFIELD,
    )
    password = models.CharField(
        'Пароль',
        max_length=LENGTH_CHARFIELD,
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'{self.username} - {self.email}'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')
