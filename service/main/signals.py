from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import *

@receiver(post_save, sender=Banner)
def send_banner_on_create(sender, instance, created, **kwargs):
    if created:
        send_banner_to_telegram.apply_async(args=[instance.id])
