import asyncio

import psycopg2 as pg
from windyquery import DB
from retrying import retry


class PostgresClient:
    def __init__(self, db_uri, cursor_factory=None):
        self._db_uri = db_uri
        self._connection = None
        self._cursor_factory = cursor_factory

    def execute(self, query, args=None):
        result = []
        with self._cursor() as my_cursor:
            my_cursor.execute(query, args)
            try:
                result = my_cursor.fetchall()

            except pg.ProgrammingError:
                pass

        return result

    def execute_with_transactions(self, list_of_queries_with_args):
        with self._cursor(autocommit=False) as my_cursor:
            try:
                for query_with_arg in list_of_queries_with_args:
                    query = query_with_arg[0]
                    args = query_with_arg[1]
                    my_cursor.execute(query, args)
                self._connection.commit()
            except Exception as exc:
                self._connection.rollback()
                raise exc

    def _cursor(self, retries=True, autocommit=True):
        if retries:
            self._connection = self._unreliable_connection()
        else:
            self._connection = self._connect()

        self._connection.autocommit = autocommit
        return self._connection.cursor()

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
    def _unreliable_connection(self):
        return self._connect()

    def _connect(self):
        return pg.connect(self._db_uri, cursor_factory=self._cursor_factory)


class AsyncPostgresClient:
    def __init__(self, db_connection_dto):
        self._db_connection_dto = db_connection_dto
        self._connection = None
        if all(db_connection_dto.values()):
            asyncio.get_event_loop().run_until_complete(self._connect())

    async def _connect(self):
        self._connection = DB()
        await self._connection.connect(self._db_connection_dto['database'], self._db_connection_dto, default=True)

    def get_db_connection(self):
        return self._connection

    def execute(self, query):
        return asyncio.get_event_loop().run_until_complete(query)

    def raw_execute(self, query):
        return asyncio.get_event_loop().run_until_complete(self._connection.raw(query))
