import io
import logging
import datetime
import os
import psycopg
from mamba import description, context, before, after, it
from expects import expect, equal, contain, raise_error
from doublex import Spy
from doublex_expects import have_been_called_with

from infpostgresql.client import PostgresClient

POSTGRES_HOSTNAME = os.getenv('POSTGRES_HOSTNAME')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_DB_URI = f'postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOSTNAME}:{POSTGRES_PORT}/{POSTGRES_DB}'

TEST_TABLE = 'test_table'

with description('PostgresClientTest') as self:
    with before.each:
        
        self.postgresql_client = PostgresClient(POSTGRES_DB_URI)
        self.postgresql_client.execute(
            f"DROP TABLE IF EXISTS {TEST_TABLE}"
        )
        self.postgresql_client.execute(
            f"CREATE TABLE {TEST_TABLE} (id SERIAL PRIMARY KEY, item varchar(10), size INT, active BOOLEAN, creation_date TIMESTAMP);"
        )
        self.postgresql_client.execute(
            f"INSERT INTO {TEST_TABLE}(item, size, active, creation_date) VALUES(%s, %s, %s, %s);",
            ("item_a", 40, False, datetime.datetime.fromtimestamp(100))
        )
        self.postgresql_client.execute(
            f"INSERT INTO {TEST_TABLE}(item, size, active, creation_date) VALUES(%s, %s, %s, %s);",
            ("item_b", 20, True, datetime.datetime.fromtimestamp(3700))
        )
        
    with context('FEATURE: execute'):
        with context('happy path'):
            with context('when selecting all rows'):
                with it('returns a list containing all rows'):
                    query = f"SELECT * FROM {TEST_TABLE}"

                    result = self.postgresql_client.execute(query)

                    expect(result).to(
                        equal([
                            (1, 'item_a', 40, False, datetime.datetime.fromtimestamp(100)),
                            (2, 'item_b', 20, True, datetime.datetime.fromtimestamp(3700)),
                        ]))
                    
                    

            with context('When running a query with parameters'):
                with it('logs the query'):
                    query = f"SELECT * FROM {TEST_TABLE}"

                    result = self.postgresql_client.execute(query)

                    expect(result).to(
                        equal([
                            (1, 'item_a', 40, False, datetime.datetime.fromtimestamp(100)),
                            (2, 'item_b', 20, True, datetime.datetime.fromtimestamp(3700)),
                        ]))

            with context('when counting rows'):
                with it('returns number of rows'):

                    result = self.postgresql_client.execute(f"SELECT COUNT(*) FROM {TEST_TABLE}")

                    expect(result[0][0]).to(equal(2))

            with context('when selecting non-existing rows'):
                with it('returns empty list'):
                    query = f"SELECT * FROM {TEST_TABLE} WHERE size > %s;"
                    params = (50,)

                    result = self.postgresql_client.execute(query, params)

                    expect(result).to(equal([]))

            with context('when deleting a row'):
                with before.each:
                    self.query_delete = f"DELETE FROM {TEST_TABLE} WHERE item = %s;"
                    self.params_delete = ('item_a',)

                with it('returns empty list'):

                    result = self.postgresql_client.execute(self.query_delete, self.params_delete)

                    expect(result).to(equal([]))

                with it('deletes the row'):
                    self.postgresql_client.execute(self.query_delete, self.params_delete)

                    query_select = f"SELECT * FROM {TEST_TABLE};"
                    result = self.postgresql_client.execute(query_select)

                    expect(result[0][1]).to(equal('item_b'))

            with context('when inserting a row'):
                with before.each:
                    self.query_insert = f"INSERT INTO {TEST_TABLE}(item, size, active, creation_date) VALUES(%s, %s, %s, %s);"
                    self.params_insert = ("item_c", 60, True, datetime.datetime.fromtimestamp(11000))

                with it('returns empty list'):

                    result = self.postgresql_client.execute(self.query_insert, self.params_insert)

                    expect(result).to(equal([]))

                with it('inserts the row'):
                    self.postgresql_client.execute(self.query_insert, self.params_insert)

                    query_select = f"SELECT COUNT(*) FROM {TEST_TABLE};"
                    result = self.postgresql_client.execute(query_select)

                    expect(result[0][0]).to(equal(3))

            with context('when updating a row'):
                with before.each:
                    self.query_update = f'UPDATE {TEST_TABLE} SET size = size + %s WHERE {TEST_TABLE}.item = %s;'
                    self.params_update = (10, 'item_a')

                with it('returns empty list'):

                    result = self.postgresql_client.execute(self.query_update, self.params_update)

                    expect(result).to(equal([]))

                with it('updates the row'):
                    self.postgresql_client.execute(self.query_update, self.params_update)

                    query_select = f"SELECT size FROM {TEST_TABLE} WHERE item = %s;"
                    params_select = ('item_a', )
                    result = self.postgresql_client.execute(query_select, params_select)

                    expect(result[0][0]).to(equal(50))

            with context('when executing an empty query'):
                with it('returns empty list'):
                    empty_query = ''

                    result = self.postgresql_client.execute(empty_query)

                    expect(result).to(equal([]))

        with context('unhappy path'):
            with context('when executing a query with an invalid column'):
                with it('raises exception from postgres'):
                    malformed_query = f'UPDATE {TEST_TABLE} SET size = size + %s WHERE {TEST_TABLE}.invalid_column = %s;'
                    params = (10, 'item_a')

                    def _execute_query_with_an_invalid_column():
                        self.postgresql_client.execute(malformed_query, params)

                    expect(_execute_query_with_an_invalid_column).to(
                        raise_error(psycopg.errors.UndefinedColumn, contain('column test_table.invalid_column does not exist')))

            with context('when executing a query with an invalid param'):
                with it('raises exception from postgres'):
                    query = f'SELECT * FROM {TEST_TABLE} WHERE active = %s;'
                    invalid_params = ('invalid_param',)

                    def _execute_query_with_an_invalid_param():
                        self.postgresql_client.execute(query, invalid_params)

                    expect(_execute_query_with_an_invalid_param).to(
                        raise_error(psycopg.errors.InvalidTextRepresentation, contain('invalid input syntax')))

            with context('when executing a malformed query'):
                with it('raises exception from postgres'):
                    malformed_query = f"SELEC * FROM {TEST_TABLE}"

                    def _execute_malformed_query():
                        self.postgresql_client.execute(malformed_query)

                    expect(_execute_malformed_query).to(raise_error(psycopg.errors.SyntaxError, contain('syntax error')))

    with description('PostgresClientTest (with dictionary cursor)') as self:
        with before.each:
            self.postgresql_client = PostgresClient(POSTGRES_DB_URI, cursor_factory=psycopg.rows.dict_row)
            self.postgresql_client.execute(
                f"DROP TABLE IF EXISTS {TEST_TABLE}"
            )
            self.postgresql_client.execute(
                f"CREATE TABLE {TEST_TABLE} (id SERIAL PRIMARY KEY, item varchar(10), size INT, active BOOLEAN, creation_date TIMESTAMP);"
            )
            self.postgresql_client.execute(
                f"INSERT INTO {TEST_TABLE}(item, size, active, creation_date) VALUES(%s, %s, %s, %s);",
                ("item_a", 40, False, datetime.datetime.fromtimestamp(100))
            )
            self.postgresql_client.execute(
                f"INSERT INTO {TEST_TABLE}(item, size, active, creation_date) VALUES(%s, %s, %s, %s);",
                ("item_b", 20, True, datetime.datetime.fromtimestamp(3700))
            )

        with context('FEATURE: execute'):
            with context('happy path'):
                with context('when selecting all rows'):
                    with it('returns a list containing all rows as dictionaries'):

                        query = f"SELECT * FROM {TEST_TABLE}"
                        result = self.postgresql_client.execute(query)

                        expect(result).to(
                            equal([
                                {'id': 1, 'item': 'item_a', 'size': 40, 'active': False, 'creation_date': datetime.datetime.fromtimestamp(100)},
                                {'id': 2, 'item': 'item_b', 'size': 20, 'active': True, 'creation_date': datetime.datetime.fromtimestamp(3700)},
                            ])
                        )

    with context('FEATURE: execute_with_transactions'):
        with before.each:
            query_1 = f'UPDATE {TEST_TABLE} SET size = size + %s WHERE {TEST_TABLE}.item = %s;'
            params_1 = (10, 'item_a')
            self.operation_1 = (query_1, params_1)

            query_2 = f'UPDATE {TEST_TABLE} SET size = size - %s WHERE {TEST_TABLE}.item = %s;'
            params_2 = (10, 'item_b')
            self.operation_2 = (query_2, params_2)

            query_3 = f'UPDATE {TEST_TABLE} SET size = size - %s WHERE {TEST_TABLE}.item = %s;'
            malformed_params_3 = ('invalid_number', 'item_b')
            self.failing_operation_3 = (query_3, malformed_params_3)

        with context('happy path'):
            with it('executes transaction'):
                self.postgresql_client.execute_with_transactions([self.operation_1, self.operation_2])

                expect(self.postgresql_client.execute(f"SELECT (size) FROM {TEST_TABLE};")).to(equal([(50,), (10,)]))

        with context('unhappy path'):
            with context('when one of the params is malformed'):
                with it('raises exception from postgres'):

                    def _execute_malformed_query():
                        self.postgresql_client.execute_with_transactions([self.operation_1, self.failing_operation_3])

                    expect(_execute_malformed_query).to(raise_error(psycopg.errors.InvalidTextRepresentation))

                with it('rolls back any changes made until the failure'):

                    def _execute_malformed_query():
                        self.postgresql_client.execute_with_transactions([self.operation_1, self.failing_operation_3])

                    expect(_execute_malformed_query).to(raise_error)
                    expect(self.postgresql_client.execute(f"SELECT (size) FROM {TEST_TABLE};")).to(equal([(40,), (20,)]))

    with context('FEATURE: execute with locks'):
        with before.each:
            self.fake_cursor = ContextSpy(FakeCursor())
            fake_connection = FakeConnection(self.fake_cursor)
            self.postgresql_client = FakePostgresClient(POSTGRES_DB_URI)
            self.postgresql_client._connection = fake_connection
            self.query = f"SELECT * FROM {TEST_TABLE};"

        with context('happy path'):
            with context('when executing a query'):
                with it('locks table to avoid concurrent access'):
                    self.postgresql_client.execute_with_lock(self.query, TEST_TABLE)

                    expect(self.fake_cursor.execute).to(have_been_called_with("BEGIN TRANSACTION;"))
                    expect(self.fake_cursor.execute).to(have_been_called_with(f"LOCK TABLE {TEST_TABLE} IN ACCESS EXCLUSIVE MODE;"))
                    expect(self.fake_cursor.execute).to(have_been_called_with("COMMIT TRANSACTION;"))

        with context('unhappy path'):
            with context('when Programming error arises'):
                with it('commits transaction'):
                    self.fake_cursor.fetchall = self.fake_cursor.raise_programming_error

                    self.postgresql_client.execute_with_lock(self.query, TEST_TABLE)

                    expect(self.fake_cursor.execute).to(have_been_called_with("COMMIT TRANSACTION;"))


class FakePostgresClient(PostgresClient):
    def _cursor(self, autocommit=True):
        return self._connection.cursor()


class FakeConnection:
    def __init__(self, fake_cursor):
        self._fake_cursor = fake_cursor

    def cursor(self):
        return self._fake_cursor


class FakeCursor:
    def execute(self, query, params=None):
        pass

    def fetchall(self):
        pass


# We have to override __enter__ to avoid problems with doublex context manager (https://github.com/davidvilla/python-doublex/issues/9)
class ContextSpy(Spy):
    def __enter__(self):
        return self

    def raise_programming_error(self):
        raise psycopg.errors.ProgrammingError
