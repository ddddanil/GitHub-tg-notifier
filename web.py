from aiohttp import web
import aiogram
from db import Hook, DataBaseHandler


async def handle_hook(request: web.Request) -> web.Response:
    id = request.match_info['id']
    telegram: aiogram.Dispatcher = request.app['telegram-bot']
    db = DataBaseHandler()
    hook: Hook = db.get_by_id(id)
    await telegram.bot.send_message(hook.chat, "New push")

    return web.Response()


def server():
    app = web.Application()
    app.router.add_post("/hook/{id:[a-fA-F0-9]{64}}", handle_hook)
    return app
