from enum import Enum, EnumMeta
from typing import Any, Awaitable, Callable
from janus import Queue


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

    def register_handler(self, message: Enum, callback: Callable[[Any], Awaitable[Any]]):
        if message not in self.messages:
            raise TypeError("This message cannot be registered")

        self.handlers[message].append(callback)

    async def dispatch(self):
        while True:
            message, obj = await self.queue.async_q.get()
            for cb in self.handlers[message]:
                await cb(obj)

    async def push(self, message: Enum, obj: Any):
        if message not in self.messages:
            raise TypeError("This message cannot be pushed")
        await self.queue.async_q.put((message, obj))
