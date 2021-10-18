import asyncio

from windyquery import DB


class AsyncPostgresClient:
    def __init__(self, db_connection_config):
        self._db_connection_config = db_connection_config
        self._db_connection = None
        if self._is_valid_config(self._db_connection_config):
            asyncio.get_event_loop().run_until_complete(self._connect())

    def get_db_connection(self):
        return self._db_connection

    def execute(self, query):
        return asyncio.get_event_loop().run_until_complete(query)

    def raw_execute(self, query):
        return asyncio.get_event_loop().run_until_complete(self._db_connection.raw(query))

    async def _connect(self):
        self._db_connection = DB()
        await self._db_connection.connect(self._db_connection_config['database'], self._db_connection_config, default=True)

    def _is_valid_config(self, db_connection_config):
        return all(db_connection_config.values())
