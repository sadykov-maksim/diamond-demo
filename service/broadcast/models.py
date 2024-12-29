from django.db import models
from django.utils.timezone import now

from main.models import TelegramUser


# Create your models here.
class Subscriber(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('unsubscribed', 'Unsubscribed'),
    ]

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, verbose_name="Telegram User")
    subscribed_at = models.DateTimeField(default=now, verbose_name="Дата подписки")
    status = models.CharField(
        max_length=12,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="Статус подписки"
    )

    class Meta:
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики"
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.user.username


class TelegramPost(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed'),
    ]

    title = models.CharField(max_length=255, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержимое")
    image = models.ImageField(max_length=255, verbose_name='Превью')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    publish_at = models.DateTimeField(verbose_name="Дата публикации", null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    error_message = models.TextField(null=True, blank=True, verbose_name="Сообщение об ошибке")

    class Meta:
        verbose_name = "Telegram пост"
        verbose_name_plural = "Telegram посты"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
