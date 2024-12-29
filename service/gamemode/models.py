
from django.db import models
from account.models import Account
from django.utils.timezone import now

from main.models import TelegramUser


# Create your models here.
class UserBalance(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}: {self.balance} USD"

class Bet(models.Model):
    COLOR_CHOICES = [
        ('red', 'Красное'),
        ('black', 'Чёрное'),
        ('green', 'Зелёное'),
    ]

    user = models.ForeignKey(Account, on_delete=models.CASCADE)  # Игрок
    color = models.CharField(max_length=10, choices=COLOR_CHOICES)  # Выбранный цвет
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Ставка
    created_at = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=10, choices=COLOR_CHOICES, null=True, blank=True)  # Выпавший цвет
    payout = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Выигрыш

class Room(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    host = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="rooms")
    current_users = models.ManyToManyField(Account, related_name="current_rooms", blank=True)

    def __str__(self):
        return f"Room({self.name} {self.host})"


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField(max_length=500)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="messages")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message({self.user} {self.room})"

class WheelFortune(models.Model):
    user = models.OneToOneField(TelegramUser, on_delete=models.CASCADE, related_name="fortuna")
    spins_left = models.PositiveIntegerField(default=1)
    last_spin_date = models.DateField(blank=True, null=True)

    def reset_spins_if_needed(self):
        """
        Сбрасывает количество спинов, если прошел новый день.
        """
        if self.last_spin_date != now().date():
            self.spins_left = 1
            self.last_spin_date = now().date()
            self.save()

    def use_spin(self):
        """
        Уменьшает количество спинов на 1.
        """
        if self.spins_left > 0:
            self.spins_left -= 1
            self.last_spin_date = now().date()
            self.save()
            return True
        return False

    def __str__(self):
        return f"Fortuna for {self.user.username} - Spins left: {self.spins_left}"


class UserSpinHistory(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='spin_history')
    result = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.result}"