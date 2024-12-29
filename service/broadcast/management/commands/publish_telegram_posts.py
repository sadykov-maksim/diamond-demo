import random
from logging import exception

from django.core.management.base import BaseCommand
from django.utils.timezone import now
from broadcast.models import TelegramPost
from aiogram import Bot, Dispatcher
import requests


from aiogram.client.default import DefaultBotProperties
from django.conf import settings
import asyncio

from diamond.settings import env

from broadcast.models import Subscriber


class Command(BaseCommand):
    help = 'Публикует запись по ID в Telegram, если она со статусом "scheduled" и временем публикации <= сейчас.'

    def add_arguments(self, parser):
        # Добавляем аргумент для ID записи
        parser.add_argument('post_id', type=int, help='ID записи для публикации')


    def handle(self, *args, **kwargs):
        post_id = kwargs['post_id']
        try:
            post = TelegramPost.objects.get(id=post_id)
        except TelegramPost.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Запись с ID {post_id} не найдена.'))
            return

        # Проверяем, что пост в статусе 'scheduled' и время публикации наступило
        if post.status == 'scheduled' and post.publish_at <= now():
            try:
                subscribers = Subscriber.objects.filter(status='active')
                for subscriber in subscribers:
                    asyncio.run(self.publish_to_telegram(post, subscriber.user.telegram_id, post.image.url))

                self.stdout.write(self.style.SUCCESS(f'Запись "{post.title}" успешно опубликована.'))
            except Exception as e:
                post.status = 'failed'
                post.error_message = str(e)
                post.save()
                self.stdout.write(self.style.ERROR(f'Ошибка при публикации "{post.title}": {str(e)}'))
            finally:
                post.status = 'published'
                post.published_at = now()
                post.save()
        else:
            self.stdout.write(self.style.WARNING(
                f'Запись "{post.title}" не подходит для публикации. Статус: {post.status}, время публикации: {post.publish_at}'))


    async def publish_to_telegram(self, post, sub_id, photo_url):
        """
        Публикация записи в Telegram канал через aiogram.
        """
        bot_token = env("BOT_TOKEN")
        channel_id = sub_id

        if not bot_token or not channel_id:
            raise ValueError("Не указан BOT_TOKEN или CHANNEL_ID в настройках")

        bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode='Markdown'))
        message = f"**{post.title}**\n\n{post.content}"

        try:
            if photo_url:
                await bot.send_photo(
                    chat_id=channel_id,
                    photo=photo_url,
                    caption=message,
                )
            else:
                await bot.send_message(
                    chat_id=channel_id,
                    text=message,
                )
        except Exception as e:
            raise Exception(f"Ошибка Telegram: {str(e)}")