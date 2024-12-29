from django.db import models
from django.contrib.auth.models import  AbstractUser


# Create your models here.

class Account(AbstractUser):
    """
    Model for storing ranks.
    """

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="balance")