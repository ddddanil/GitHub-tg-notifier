from configparser import ConfigParser
from functools import partial
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import *
from logging import getLogger
from db import Hook, make_id, DataBaseHandler
logger = getLogger('GitHubBot.telegram')


async def register(config: ConfigParser, message: types.Message):
    await types.ChatActions.typing()
    user = str(message.from_user.id)
    chat = str(message.chat.id)
    name = message.get_args()
    id = make_id(user, name, config["DEFAULT"]["SALT"])
    await DataBaseHandler.insert_hook(Hook(id, user, name, chat))
    return SendMessage(message.chat.id, f"Ok, add this url to your webhooks {config['web']['host'] + 'hook/' + id}")


def bot(config: ConfigParser) -> Dispatcher:
    bot = Bot(config['Telegram']['Token'])
    dispatcher = Dispatcher(bot)

    dispatcher.register_message_handler(partial(register, config), commands=["register"])

    return dispatcher
