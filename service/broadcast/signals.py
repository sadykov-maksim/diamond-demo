from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TelegramPost


@receiver(post_save, sender=TelegramPost)
def set_scheduled_status(sender, instance, **kwargs):
    """
    Изменяет статус записи на 'scheduled' после сохранения,
    если статус был 'pending'.
    """
    if instance.status == 'pending':
        instance.status = 'scheduled'
        instance.save(update_fields=['status'])