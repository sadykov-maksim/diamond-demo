from django.db import models
from main.models import TelegramUser

# Create your models here.
class WithdrawalMethod(models.Model):
    """
    Модель для хранения информации о способах вывода средств.
    """
    METHOD_CHOICES = [
        ('manual', 'Ручной вывод'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Банковский перевод'),
        ('crypto', 'Криптовалюта'),
    ]

    method_name = models.CharField(max_length=50, default="Банковские переводы", verbose_name="Название метода")
    method = models.CharField(max_length=50, choices=METHOD_CHOICES, unique=True, verbose_name="Метод")
    description = models.TextField(blank=True, null=True, verbose_name="Описание", help_text="Описание способа вывода")
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Минимальная сумма", help_text="Минимальная сумма для вывода")
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="Процент комиссии", help_text="Процент комиссии")
    fixed_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Фиксированная комиссия", help_text="Фиксированная комиссия")

    def __str__(self):
        return self.method_name

    class Meta:
        verbose_name = "Способ вывода"
        verbose_name_plural = "Способы вывода"


class BankTransferOption(models.Model):
    """
    Модель для хранения настроек банковских переводов для вывода средств.
    """
    withdrawal_method = models.ForeignKey(WithdrawalMethod, on_delete=models.CASCADE, limit_choices_to={'method': 'bank_transfer'}, related_name="bank_options", verbose_name="Метод вывода")
    bank_name = models.CharField(max_length=50, verbose_name="Название банка", help_text="Название банка, например, Сбер или Альфа")
    bank_code = models.CharField(max_length=20, blank=True, verbose_name="Код банка", help_text="Код банка или иная идентификация, если требуется")
    additional_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="Дополнительная комиссия", help_text="Дополнительная комиссия для конкретного банка")

    def __str__(self):
        return f"{self.bank_name} ({self.withdrawal_method.method_name})"

    class Meta:
        verbose_name = "Банковский перевод"
        verbose_name_plural = "Банковские переводы"


class CryptoTransferOption(models.Model):
    """
    Модель для хранения настроек вывода в криптовалюте.
    """
    withdrawal_method = models.ForeignKey(WithdrawalMethod, on_delete=models.CASCADE, limit_choices_to={'method': 'crypto'}, related_name="crypto_options", verbose_name="Метод вывода")
    crypto_name = models.CharField(max_length=50, verbose_name="Название криптовалюты", help_text="Например, Bitcoin или Ethereum")
    crypto_code = models.CharField(max_length=20, blank=True, verbose_name="Код криптовалюты", help_text="Код или сокращение криптовалюты, например BTC")
    additional_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, verbose_name="Дополнительная комиссия", help_text="Дополнительная комиссия для конкретной криптовалюты")

    def __str__(self):
        return f"{self.crypto_name} ({self.withdrawal_method.method_name})"

    class Meta:
        verbose_name = "Криптовалютный перевод"
        verbose_name_plural = "Криптовалютные переводы"


class WithdrawalRequest(models.Model):
    """
    Модель для хранения информации о заявках на вывод средств.
    """
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
        ('completed', 'Завершена'),
    ]

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='withdrawal_requests', verbose_name='Пользователь')
    amount = models.DecimalField(max_digits=10,  decimal_places=2, verbose_name='Сумма вывода', help_text='Сумма, указанная для вывода')
    method = models.CharField(max_length=50, verbose_name='Метод вывода', help_text='Способ вывода средств (например, Криптовалюта, Банковская карта)')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name='Статус заявки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    notes = models.TextField(blank=True, null=True, verbose_name='Примечания', help_text='Примечания или комментарии администратора')

    def __str__(self):
        return f"Заявка #{self.id} от {self.user} на сумму {self.amount} руб."

    class Meta:
        verbose_name = 'Заявка на вывод средств'
        verbose_name_plural = 'Заявки на вывод средств'
        ordering = ['-created_at']
