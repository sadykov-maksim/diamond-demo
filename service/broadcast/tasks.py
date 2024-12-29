from celery import shared_task
from django.core.management import call_command
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from diamond.settings import env
from gamemode.models import WheelFortune
from main.management.commands.tgbot.keyboards.inline import game_keyboard
from .models import TelegramPost
from django.utils.timezone import now

@shared_task
def process_scheduled_posts():
    """
    Проверяет все записи со статусом 'scheduled'.
    Публикует записи, время публикации которых наступило.
    Планирует автоматическое выполнение для записей с будущей датой.
    """
    posts = TelegramPost.objects.filter(status='scheduled')

    for post in posts:
        if post.publish_at <= now():
            # Если время публикации наступило
            publish_scheduled_posts(post.id)


@shared_task
def publish_scheduled_posts(post_id):
    """
    Публикует запись со статусом 'scheduled' и временем публикации <= сейчас.
    """
    post = TelegramPost.objects.filter(id=post_id).first()
    try:
        call_command('publish_telegram_posts', post.id)
        post.status = 'published'
    except Exception as e:
        post.status = 'failed'
        post.error_message = str(e)
    post.save()

@shared_task
def notify_users_about_spins():
    """
    Уведомляет пользователей о доступных спинах ежедневно.
    """
    today = now().date()
    fortunes = WheelFortune.objects.all()
    for fortuna in fortunes:
        try:
            # Сброс спинов, если начался новый день
            if fortuna.last_spin_date != today:
                fortuna.spins_left = 1
                fortuna.last_spin_date = today
                fortuna.save()

            # Отправляем уведомление только если спины доступны
            if fortuna.spins_left > 0:
                asyncio.run(_notify_users_about_spins_async(fortuna.user.telegram_id))
        except Exception as e:
            # Обработайте исключения (логирование или другой механизм)
            print(f"Ошибка при уведомлении пользователя {fortuna.user.username}: {str(e)}")


async def _notify_users_about_spins_async( telegram_user_id):
    """
    Асинхронная логика уведомления пользователей.
    """
    bot_token = env("BOT_TOKEN")
    button_text = "Посетить сайт"
    button_url = "https://example.com"

    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode='Markdown'))

    await bot.send_message(chat_id=telegram_user_id, text=f"Привет, 🎰 У вас доступен 1 бесплатный спин на сегодня! Не забудьте использовать его.", reply_markup=game_keyboard(), parse_mode="Markdown")
