import asyncio
from enum import Enum, auto
import pytest
from githubbot.msg_queue import MsgQueue


class TestMsgQueue:

    @pytest.mark.asyncio
    async def test_queue(self):

        class Message(Enum):
            Huh = auto()
            Yes = auto()
            No = auto()

        queue = MsgQueue(Message)

        async def huhhuh(huh: str):
            assert huh == "huh"

        async def yes(thing: bool):
            assert thing

        async def no(thing: bool):
            assert not thing

        queue.register_handler(Message.Huh, huhhuh)
        queue.register_handler(Message.Yes, yes)
        queue.register_handler(Message.No, no)

        queue_fut = asyncio.ensure_future(queue.dispatch())

        await queue.push(Message.Huh, "huh")
        await queue.push(Message.Yes, True)
        await queue.push(Message.No, None)
        await queue.push(Message.Yes, False)

        queue_fut.cancel()
