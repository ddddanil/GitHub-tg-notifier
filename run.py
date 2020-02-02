from configparser import ConfigParser
from functools import partial
from aiohttp.web import run_app
from asyncio import ensure_future
from aiogram.utils.executor import start_polling
import logging
from tg import bot
from web import server
logger = logging.getLogger("GitHubBot.main")


def prepare_logging():
    global logger
    simple_formatter = logging.Formatter('%(levelname)-8s %(name)-24s: %(message)s')
    wide_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s\n\t-= %(message)s =-')
    debuglog = logging.StreamHandler()
    debuglog.setLevel(logging.DEBUG)
    debuglog.setFormatter(simple_formatter)

    master_logger = logging.getLogger('GitHubBot')
    master_logger.setLevel(logging.DEBUG)

    master_logger.addHandler(debuglog)

    logger = logging.getLogger('GitHubBot.main')


def get_config() -> ConfigParser:
    config = ConfigParser()
    config.read("config.ini")
    return config


async def start_bot(config, app):
    telegram = bot(config)
    app['telegram-bot'] = telegram
    start_polling(telegram, skip_updates=True)
    pass


async def stop_bot(app):
    # app['telegram-bot'].stop()
    pass


def main():
    prepare_logging()
    config = get_config()

    web_server = server()

    web_server.on_startup.append(partial(start_bot, config))
    web_server.on_shutdown.append(stop_bot)

    return web_server


if __name__ == '__main__':
    web_server = main()
    run_app(web_server)


def init_func(argv):
    web_server = main()
    return web_server
