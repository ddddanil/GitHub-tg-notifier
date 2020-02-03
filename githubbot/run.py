from configparser import ConfigParser
from functools import partial
from aiohttp.web import run_app
from asyncio import ensure_future
from asyncio import get_event_loop
import logging
from tg import bot
from web import server
from db import DataBaseHandler
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


async def build():
    prepare_logging()
    config = get_config()

    db = DataBaseHandler(config)
    await db.create_table()


    telegram = bot(config)
    web_server = server(telegram)
    web_server['telegram-bot'] = telegram

    return web_server


if __name__ == '__main__':
    web_server = get_event_loop().run_until_complete(build())
    run_app(web_server)


def init_func(argv):
    web_server = get_event_loop().run_until_complete(build())
    return web_server
