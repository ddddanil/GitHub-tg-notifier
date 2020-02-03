import asyncio
from enum import Enum, auto
import pytest
from githubbot.msg_queue import MsgQueue


class TestMsgQueue:

    @pytest.fixture
    def messages(self):
        class Message(Enum):
            Huh = auto()
            Yes = auto()
            No = auto()

        return Message

    @pytest.yield_fixture
    def message_queue(self, messages):
        queue = MsgQueue(messages)

        queue_fut = asyncio.ensure_future(queue.dispatch())
        yield queue
        queue_fut.cancel()

    @pytest.mark.asyncio
    async def test_queue(self, message_queue, messages):

        async def huhhuh(huh: str):
            assert huh == "huh"

        async def yes(thing: bool):
            assert thing

        async def no(thing: bool):
            assert not thing

        message_queue.register_handler(messages.Huh, huhhuh)
        message_queue.register_handler(messages.Yes, yes)
        message_queue.register_handler(messages.No, no)

        await message_queue.push(messages.Huh, "huh")
        await message_queue.push(messages.Yes, True)
        await message_queue.push(messages.No, None)
        await message_queue.push(messages.Yes, False)
