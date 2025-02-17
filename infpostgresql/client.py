from psycopg_pool import ConnectionPool
from retrying import retry
from psycopg import OperationalError

from infcommon import logger

from infpostgresql.debugger import debug_sql_call, debug_sql_transaction_calls


def _retry_on_specific_exception(exception):
    return isinstance(exception, OperationalError)


class PostgresClient:
    def __init__(self, db_uri, cursor_factory=None, min_conn=1, max_conn=10):
        self._db_uri = db_uri
        self._cursor_factory = cursor_factory
        self._pool = ConnectionPool(
            conninfo=self._db_uri,
            min_size=min_conn,
            max_size=max_conn,
            timeout=10
        )

    @debug_sql_call
    @retry(retry_on_exception=_retry_on_specific_exception, wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
    def execute(self, query, params=None):
        result = []
        with self._pool.connection() as conn:
            try:
                with conn.cursor(row_factory=self._cursor_factory) as cur:
                    cur.execute(query, params)
                    if cur.description:
                        result = cur.fetchall()
                    conn.commit()
            except Exception as e:
                if conn.closed:
                    logger.info("PostgresClient: Connection is closed. Cannot rollback.")
                else:
                    conn.rollback()
                logger.error(f"PostgresClient: Error in execute: {e}")
                raise e
        return result

    @retry(retry_on_exception=_retry_on_specific_exception, wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
    def execute_with_lock(self, query, table, params=None):
        result = []
        with self._pool.connection() as conn:
            try:
                with conn.cursor(row_factory=self._cursor_factory) as cur:
                    cur.execute("BEGIN TRANSACTION;")
                    cur.execute(f"LOCK TABLE {table} IN ACCESS EXCLUSIVE MODE;")
                    cur.execute(query, params)

                    if cur.description:
                        result = cur.fetchall()

                    conn.commit()
            except Exception as e:
                if conn.closed:
                    logger.info("PostgresClient: Connection is closed. Cannot rollback.")
                else:
                    conn.rollback()
                logger.error(f"PostgresClient: Error in execute with lock: {e}")
                raise e
        return result

    @debug_sql_transaction_calls
    @retry(retry_on_exception=_retry_on_specific_exception, wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5)
    def execute_with_transactions(self, list_of_queries_with_params):
        with self._pool.connection() as conn:
            try:
                with conn.cursor(row_factory=self._cursor_factory) as cur:
                    for query_with_params in list_of_queries_with_params:
                        query = query_with_params[0]
                        params = query_with_params[1]
                        cur.execute(query, params)
                    conn.commit()
            except Exception as e:
                if conn.closed:
                    logger.info("PostgresClient: Connection is closed. Cannot rollback.")
                else:
                    conn.rollback()
                logger.error(f"PostgresClient: Error in execute with transaction: {e}")
                raise e
