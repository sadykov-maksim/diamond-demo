from django.core.exceptions import ValidationError
from django.db import models
from main.models import TelegramUser


# Create your models here.
class TicketType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    callback = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тип тикета'
        verbose_name_plural = 'Типы тикетов'

class SupportTicket(models.Model):
    TICKET_TYPES = [
        ('game', 'Проблемы с игрой'),
        ('bonus', 'Проблемы с бонусами/начислениями'),
        ('withdraw', 'Проблемы с выводом средств'),
        ('account', 'Проблемы с настройками аккаунта'),
        ('functionality', 'Ошибки с функционалом бота'),
        ('events', 'Проблемы с игровыми событиями'),
        ('improvement', 'Обращения по улучшению игрового процесса'),
        ('other', 'Другое'),
    ]

    STATUS_CHOICES = [
        ('open', 'Открыт'),
        ('in_progress', 'В работе'),
        ('closed', 'Закрыт'),
    ]

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='tickets', verbose_name='Пользователь')
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE, default='login')

    description = models.TextField(verbose_name='Описание проблемы')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open', verbose_name='Статус тикета')
    answer = models.TextField(verbose_name='Ответ администратора', help_text="Решение проблемы", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    @classmethod
    def create_ticket(cls, user, ticket_type, description):
        if not ticket_type or not description:
            raise ValidationError("Тема и описание тикета не могут быть пустыми.")

        telegram_user = TelegramUser.objects.filter(telegram_id=user).first()
        ticket_typed = TicketType.objects.get(callback=ticket_type)
        ticket = cls.objects.create(
            user=telegram_user,
            ticket_type=ticket_typed,
            description=description
        )
        return ticket

    def __str__(self):
        return f"({self.get_status_display()})"

    class Meta:
        verbose_name = 'Тикет поддержки'
        verbose_name_plural = 'Тикеты поддержки'
        ordering = ['-created_at']


class FAQ(models.Model):
    question = models.CharField(max_length=255, unique=True)
    answer = models.TextField()
    callback_data = models.CharField(default="callback_data", max_length=255)
    helpful_count = models.PositiveIntegerField(default=0)
    not_helpful_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question

    @classmethod
    def get_faq_list(cls):
        faq = FAQ.objects.filter(is_active=True)
        return faq

    @classmethod
    def get_questions_by_filter(cls, callback_data):
        faq = cls.objects.filter(callback_data=callback_data).first()
        return faq.id

    @classmethod
    def get_question(cls, callback_data):
        faq = cls.objects.filter(callback_data=callback_data).first()
        return faq


    def add_feedback(self, callback_data=None, user=None, helpful=True):
        """Добавляет отзыв: помогло или не помогло."""
        user = TelegramUser.objects.get(telegram_id=user)
        faq = self.get_questions_by_filter(callback_data)
        if helpful:
            FAQFeedback.create_feedback(user, faq, helpful)
        else:
            FAQFeedback.create_feedback(user, faq, helpful)
        self.save()

    @property
    def helpful_percentage(self):
        """Вычисляет процент положительных отзывов."""
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0
        return round((self.helpful_count / total) * 100, 2)

class FAQFeedback(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE)
    is_helpful = models.BooleanField(null=True)

    @classmethod
    def create_feedback(cls, user, faq, is_helpful):
        feedback, created = cls.objects.update_or_create(
            user=user,
            faq_id=faq,
            defaults={'is_helpful': is_helpful}
        )
        return feedback, created

    @classmethod
    def feedback_exists(cls, user, question):
        faq = FAQ.get_questions_by_filter(question)
        feedback_exists = FAQFeedback.objects.filter(user__telegram_id=user, faq_id=faq).exists()
        return feedback_exists

    class Meta:
        unique_together = ('user', 'faq')

    def __str__(self):
        return f"Feedback from {self.user.username} on FAQ: {self.faq.question}"