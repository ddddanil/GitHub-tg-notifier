from aiogram import Dispatcher
from aiogram.dispatcher.webhook import WebhookRequestHandler
from aiohttp import web
from functools import partial
from logging import getLogger
logger = getLogger('GitHubBot.telegram')

class HookExecutor:
    def __init__(self, dispatcher, **kwargs):
        self.dispatcher = dispatcher
        self.skip_updates = kwargs['skip_updates']
        self.check_ip = kwargs['check_ip']
        self.retry_after = kwargs['retry_after']
        self.loop = kwargs['loop']
        self.on_startup = kwargs['on_startup']
        self.on_shutdown = kwargs['on_shutdown']
        self._web_app = None
        self._frozen = False

    @property
    def _assert_not_frozen(self):
        if self._frozen:
            raise RuntimeError("Execution is frozen!")

    @property
    def web_app(self):
        return self._web_app

    def _setup(self, webhook_path='/', handler=WebhookRequestHandler):
        self._assert_not_frozen()
        self._frozen = True

        if self.web_app: return

        self._web_app = web.Application()

        self._web_app['RETRY_AFTER'] = self.retry_after | None

        self._web_app.router.add_route('*', webhook_path, handler)

        async def _wrap_callback(cb, _):
            return await cb(self.dispatcher)

        for callback in self.on_startup:
            self._web_app.on_startup.append(partial(_wrap_callback, callback))

        for callback in self.on_shutdown:
            self._web_app.on_shutdown.append(partial(_wrap_callback, callback))

        self._web_app['APP_EXECUTOR'] = self
        self._web_app['BOT_DISPATCHER'] = self.dispatcher
        self._web_app['_check_ip'] = self.check_ip
