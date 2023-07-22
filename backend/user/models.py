from django.contrib.auth.models import AbstractUser
from django.db import models

class NewUser(AbstractUser):
    first_name = models.CharField('Имя', max_length=150, blank=True, null=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True, null=True)
    username = models.CharField('Уникальный юзернейм', unique=True, max_length=150)
    email = models.EmailField('Почта', unique=True, max_length=254)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} ({self.pk})'


