import aiosqlite
from collections import namedtuple
from configparser import ConfigParser
from random import randint
from hashlib import sha256
from singleton import Singleton


Hook = namedtuple('Hook', 'id user name chat')


class DataBaseHandler(metaclass=Singleton):
    __slots__ = ["db", "queue"]

    def __init__(self, config: ConfigParser):
        self.db = config['DATABASE']['PATH']

    async def create_table(self):
        async with aiosqlite.connect(self.db) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS hooks (
                 id text,
                 user text,
                 name text,
                 chat text
            """)
            await db.commit()

    async def get_for_user(self, user: str):
        async with aiosqlite.connect(self.db) as db:
            async with db.execute("SELECT * FROM hooks WHERE user=?", (user, )) as cursor:
                return [Hook(*row) async for row in cursor]

    async def get_by_user_and_name(self, user: str, name: str):
        async with aiosqlite.connect(self.db) as db:
            async with db.execute("SELECT * FROM hooks WHERE user=? AND name=?", (user, name)) as cursor:
                return Hook(*cursor.fetch_one())

    async def get_by_id(self, id: str):
        async with aiosqlite.connect(self.db) as db:
            async with db.execute("SELECT * FROM hooks WHERE id=?", (id, )) as cursor:
                return Hook(*cursor.fetch_one())

    async def insert_hook(self, hook: Hook):
        async with aiosqlite.connect(self.db) as db:
            await db.execute("INSERT INTO hooks VALUES (?,?,?,?)", hook)
            await db.commit()

    async def update_chat(self, id: str, new_chat: str):
        async with aiosqlite.connect(self.db) as db:
            await db.execute("UPDATE hooks SET chat=? WHERE id=?", (new_chat, id))
            await db.commit()


def make_id(user: str, name: str, salt: str):
    return sha256(str(randint()) + user + name + salt).hex_digest()
