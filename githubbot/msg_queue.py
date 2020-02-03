from asyncio import ensure_future, Task
from enum import Enum, EnumMeta
from typing import Any, Awaitable, Callable
from janus import Queue
from logging import getLogger
logger = getLogger("GitHubBot.MsgQueue")


class MsgQueue:
    def __init__(self, messages: EnumMeta):
        if not isinstance(messages, EnumMeta):
            raise TypeError("Messages have to be derived from an Enum type")

        self.messages_type = type(messages)
        self.messages = messages

        self.handlers = {}
        for msg in list(messages):
            self.handlers[msg] = []

        self.queue = Queue()
        self.results = Queue()
        self.join_task = None

    def register_handler(self, message: Enum, callback: Callable[[Any], Awaitable[Any]]):
        if message not in self.messages:
            raise TypeError("This message cannot be registered")

        self.handlers[message].append(callback)

    async def dispatch(self):
        if not self.join_task:
            self.join_task = ensure_future(self.join())
        while True:
            message, obj = await self.queue.async_q.get()
            for cb in self.handlers[message]:
                await self.results.async_q.put(ensure_future(cb(obj)))

    async def join(self):
        while True:
            task: Task = await self.results.async_q.get()
            if task.done():
                e = task.exception()
                if e:
                    logger.error("Handler task has failed", exc_info=e)
                else:
                    continue
            else:
                await self.results.async_q.put(task)

    async def push(self, message: Enum, obj: Any):
        if message not in self.messages:
            raise TypeError("This message cannot be pushed")
        await self.queue.async_q.put((message, obj))
