import uuid
from datetime import timezone

from django.db import models

# Create your models here.
class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField()
    nickname = models.CharField(max_length=50, unique=True, null=True, blank=True)
    username = models.CharField(max_length=50)
    phone = models.CharField(max_length=50, null=True, blank=True)
    referer = models.PositiveIntegerField(null=True, blank=True)
    language = models.CharField(max_length=50, null=True, blank=True)
    date_birth = models.DateField(auto_now=False, auto_now_add=True)
    date_joined = models.DateField(auto_now=False, auto_now_add=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    @classmethod
    def count(cls, telegram_id):
        return cls.objects.filter(referer=telegram_id).count()

    @classmethod
    def get_by_telegram_id(cls, telegram_id):
        return cls.objects.get(telegram_id=telegram_id)

    def str(self):
        return self.username

    class Meta:
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'


class InviteCode(models.Model):
    code = models.TextField(max_length=512, unique=True, help_text="Уникальный пригласительный код")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Дата создания кода")
    expires_at = models.DateTimeField(help_text="Дата и время окончания действия кода")
    user = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="used_invite_codes", help_text="Пользователь, который использовал код")

    def __str__(self):
        return f"Invite Code {self.code} - User: "

    def mark_as_used(self, user: TelegramUser):
        """Метод для пометки кода как использованного, с проверкой на срок действия"""
        if timezone.now() > self.expires_at:
            raise ValueError("Этот код уже истек и не может быть использован.")

        self.used_by = user
        self.used_at = timezone.now()
        self.save()

    def is_valid(self):
        """Проверяет, доступен ли код для использования, с учетом времени"""
        return timezone.now() <= self.expires_at

class GameHistory(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    game_type = models.CharField(max_length=50)  # Например, 'Фортуна', 'Рулетка' и т.д.
    bet_amount = models.DecimalField(max_digits=10, decimal_places=2)
    win_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    result = models.CharField(max_length=20)  # Например, 'Победа' или 'Проигрыш'
    played_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.game_type} - {self.result}"

    class Meta:
        verbose_name = 'Game History'
        verbose_name_plural = 'Game Histories'

#class Banner(models.Model):
#    """Banners"""
#    name = models.CharField(max_length=50)
#    image = models.ImageField(upload_to='banners/', max_length=60, null=True, blank=True)
#    description = models.TextField()
#
#    def __str__(self):
#        return self.name
#
#    class Meta:
#        verbose_name = 'Banner'
#        verbose_name_plural = 'Banners'

class Banner(models.Model):
    """Banners"""
    name = models.CharField(max_length=50)
    level = models.PositiveIntegerField()  # Уровень, где хранится изображение
    file_id = models.CharField(max_length=255, blank=True, null=True)  # Добавленное поле для хранения file_id
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания изображения
    image = models.ImageField(upload_to='banners/')  # Путь загрузки изображения
    status = models.CharField(max_length=50, choices=[  # Статус баннера
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ], default='active')

    def __str__(self):
        return f"Banner ID: {self.id}, Level: {self.level}, Status: {self.status}"

class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount to be added/discounted
    is_active = models.BooleanField(default=True)  # Status of the promo code
    used_by = models.ManyToManyField(TelegramUser, blank=True)  # Users who have used the promo code

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'Promo Code'
        verbose_name_plural = 'Promo Codes'

class TransactionHistory(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"

    class Meta:
        verbose_name = 'Transaction History'
        verbose_name_plural = 'Transaction Histories'

class Game(models.Model):
    name = models.CharField(max_length=100)
    banner = models.ImageField(upload_to='game/', max_length=100, null=True, blank=True, verbose_name="Баннер")
    state = models.CharField(max_length=50)
    code = models.CharField(max_length=50, null=True, blank=True, unique=True)
    mini_link = models.URLField(verbose_name="Ссылка на мини-игру")
    description = models.TextField(null=True, blank=True)  # Краткое описание игры
    min_bet = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Минимальная ставка для игры
    max_bet = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Максимальная ставка
    created_at = models.DateTimeField(auto_now_add=True)  # Дата добавления игры
    is_active = models.BooleanField(default=True)  # Флаг, активна ли игра

    def save(self, *args, **kwargs):
        # Генерация кода только если он еще не установлен
        if not self.code:
            self.code = self.generate_unique_code()
        super(Game, self).save(*args, **kwargs)

    def generate_unique_code(self):
        # Генерация уникального индикатора с использованием UUID и усечения до 8 символов
        code = str(uuid.uuid4()).split('-')[0]
        # Проверяем уникальность кода
        while Game.objects.filter(code=code).exists():
            code = str(uuid.uuid4()).split('-')[0]
        return code

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'

class Message(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.PROTECT)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return self.message

    class Meta:
        db_table = 'message'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'


class Category(models.Model):
    name = models.CharField(max_length=100)

class ItemGroup(models.Model):
    category = models.ForeignKey(Category, related_name='groups', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    probability = models.FloatField(help_text='Шанс выпадения (в процентах)')
    status = models.BooleanField(default=False)

class Item(models.Model):
    group = models.ForeignKey(ItemGroup, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)



