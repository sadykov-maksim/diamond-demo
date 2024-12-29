import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command as cmd
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from main.management.commands.tgbot.config import load_config, Config
from main.management.commands.tgbot.handlers import routers_list


from main.management.commands.tgbot.middlewares.config import ConfigMiddleware
from main.management.commands.tgbot.services import broadcaster

from django.core.management.base import BaseCommand

from diamond.settings import env


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        try:
            asyncio.run(main())
        except (KeyboardInterrupt, SystemExit):
            logging.error("Бот був вимкнений!")


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Бот був запущений")


def register_global_middlewares(dp: Dispatcher, config: Config, session_pool=None):
    """
    Register global middlewares for the given dispatcher.
    Global middlewares here are the ones that are applied to all the handlers (you specify the type of update)

    :param dp: The dispatcher instance.
    :type dp: Dispatcher
    :param config: The configuration object from the loaded configuration.
    :param session_pool: Optional session pool object for the database using SQLAlchemy.
    :return: None
    """
    middleware_types = [
        ConfigMiddleware(config),
        # DatabaseMiddleware(session_pool),
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def setup_logging():
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    It sets the log level to INFO and configures a basic colorized log for
    output. The log format includes the filename, line number, log level,
    timestamp, logger name, and log message.

    Returns:
        None

    Example usage:
        setup_logging()
    """
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def get_storage(config):
    """
    Return storage based on the provided configuration.

    Args:
        config (Config): The configuration object.

    Returns:
        Storage: The storage object based on the configuration.

    """

    return MemoryStorage()


async def main():
    setup_logging()

    config = load_config()
    storage = get_storage(config)

    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher(storage=storage)

    dp.include_routers(*routers_list)

    #dp.pre_checkout_query.register(pre_checkout_handler)
    #dp.message.register(pay_support_handler, cmd(commands="paysupport"))
    register_global_middlewares(dp, config)

    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot,  allowed_updates=dp.resolve_used_update_types())
