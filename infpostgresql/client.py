import psycopg
from retrying import retry


class PostgresClient:
    def __init__(self, db_uri, cursor_factory=None):
        self._db_uri = db_uri
        self._connection = None
        self._cursor_factory = cursor_factory

    def execute(self, query, params=None):
        result = []
        with self._cursor() as cur:
            cur.execute(query, params)
            try:
                result = cur.fetchall()

            except psycopg.ProgrammingError:
                pass

        return result

    def execute_with_lock(self, query, table, params=None):
        result = []
        with self._cursor() as cur:
            cur.execute("BEGIN TRANSACTION;")
            cur.execute(f"LOCK TABLE {table} IN ACCESS EXCLUSIVE MODE;")
            cur.execute(query, params)
            try:
                result = cur.fetchall()
                cur.execute("COMMIT TRANSACTION;")

            except psycopg.ProgrammingError:
                cur.execute("COMMIT TRANSACTION;")

        return result

    def execute_with_transactions(self, list_of_queries_with_params):
        with self._cursor(autocommit=False) as cur:
            try:
                for query_with_params in list_of_queries_with_params:
                    query = query_with_params[0]
                    params = query_with_params[1]
                    cur.execute(query, params)
                self._connection.commit()
            except Exception as exc:
                self._connection.rollback()
                raise exc

    def _cursor(self, autocommit=True):
        self._connection = self._unreliable_connection(autocommit)
        return self._connection.cursor()

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
    def _unreliable_connection(self, autocommit):
        return psycopg.connect(
            self._db_uri,
            autocommit=autocommit,
            row_factory=self._cursor_factory,
        )
