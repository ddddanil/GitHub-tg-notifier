from aiohttp import web
import aiogram
from .db import Hook, DataBaseHandler
from .tg_executor import HookExecutor
from logging import getLogger
logger = getLogger("GitHubBot.web")


async def handle_hook(request: web.Request) -> web.Response:
    id = request.match_info['id']
    telegram: aiogram.Dispatcher = request.app['telegram-bot']
    db = DataBaseHandler()
    hook: Hook = await db.get_by_id(id)
    await telegram.bot.send_message(hook.chat, "New push")

    return web.Response()


def github_hooks() -> web.Application:
    app = web.Application()
    app.router.add_post("/{id:[a-fA-F0-9]{64}}", handle_hook)
    return app


def telegram_hooks(dispatcher: aiogram.Dispatcher) -> web.Application:
    executor = HookExecutor(dispatcher)
    return executor.web_app()


def server(tg: aiogram.Dispatcher) -> web.Application:
    app = web.Application()
    app.add_subapp("github/", github_hooks())
    app.add_subapp("tg/", telegram_hooks(tg))
    return app
