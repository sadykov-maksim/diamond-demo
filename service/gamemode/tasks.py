from django.utils.timezone import now
from celery import shared_task
from .models import *


@shared_task
def reset_all_spins():
    today = now().date()
    for fortuna in WheelFortune.objects.all():
        if fortuna.last_spin_date != today:
            fortuna.spins_left = 1
            fortuna.last_spin_date = today
            fortuna.save()