import asyncio

from aiogram import Bot
from aiogram.types import InputFile
from celery import shared_task

from django.core.management import call_command
from aiogram.types import FSInputFile
from diamond import settings
from .models import Banner


@shared_task
def send_hello():
    return "Привет"

@shared_task
def run_management_command():
    """
    Запускает Django management-команду через subprocess.
    """
    call_command('bot')




async def send_photo_and_get_file_id(bot, banner_id, file_path):
    photo_file = FSInputFile(path=file_path, filename=f"{banner_id}.jpg")
    # Отправка фото и получение информации о файле
    message = await bot.send_photo(chat_id=settings.TELEGRAM_CHAT_ID, photo=photo_file)

    # Получаем информацию о файле
    file_info = await bot.get_file(message.photo[-1].file_id)  # Получаем file_id для последнего фото
    return file_info.file_id


@shared_task
def send_banner_to_telegram(banner_id):
    # Получаем баннер по ID
    banner = Banner.objects.get(id=banner_id)

    token = settings.TELEGRAM_BOT_TOKEN
    bot = Bot(token=token)
    file_path = banner.image.path

    # Запуск асинхронной функции внутри синхронной Celery задачи
    file_id = asyncio.run(send_photo_and_get_file_id(bot, banner_id, file_path))

    # Обновляем file_id в модели
    banner.file_id = file_id
    banner.save()
