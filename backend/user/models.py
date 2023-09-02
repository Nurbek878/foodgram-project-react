from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from rest_framework.exceptions import ParseError


class NewUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email=None, password=None, **extra_fields):
        if not email:
            raise ParseError('Укажите email')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)


class NewUser(AbstractUser):
    first_name = models.CharField('Имя', max_length=150,
                                  blank=True, null=True)
    last_name = models.CharField('Фамилия', max_length=150,
                                 blank=True, null=True)
    username = models.CharField('Уникальный юзернейм',
                                unique=True, max_length=150)
    email = models.EmailField('Почта', unique=True, max_length=254)
    subscribed_to = models.ManyToManyField(
        'self',
        symmetrical=False,
        through_fields=('subscriber', 'subscribe'),
        through='Subscription',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']
    objects = NewUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} ({self.pk})'


class Subscription(models.Model):
    subscriber = models.ForeignKey(NewUser, on_delete=models.CASCADE,
                                   related_name='subscription_set')
    subscribe = models.ForeignKey(NewUser, on_delete=models.CASCADE,
                                  related_name='subscribed_by')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        models.UniqueConstraint(fields=['subscriber', 'subscribe'],
                                name='unique_subscriber_subscribe')

    def __str__(self):
        return f'{self.subscriber} подписан на {self.subscribe}'
