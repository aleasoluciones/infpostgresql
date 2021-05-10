from mamba import description, context, before, it
from expects import expect, have_len, equal, contain, raise_error

import datetime
import os

from psycopg2 import errors as psycopg2_errors

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
        self.postgresql_client.execute(f"DROP TABLE IF EXISTS {TEST_TABLE}")
        self.postgresql_client.execute(
            f"CREATE TABLE {TEST_TABLE} (id SERIAL, item varchar(10), size INT, active BOOLEAN, date TIMESTAMP, PRIMARY KEY (id));"
        )
        self.postgresql_client.execute(f"INSERT INTO {TEST_TABLE}(item, size, active, date) VALUES(%s, %s, %s, %s);",
                                       ("item_a", 40, False, datetime.datetime.fromtimestamp(100)))
        self.postgresql_client.execute(f"INSERT INTO {TEST_TABLE}(item, size, active, date) VALUES(%s, %s, %s, %s);",
                                       ("item_b", 20, True, datetime.datetime.fromtimestamp(3700)))

    with context('FEATURE: execute'):
        with context('happy path'):
            with context('when selecting all rows'):
                with it('returns a list containing all values'):
                    query = f"SELECT * FROM {TEST_TABLE}"

                    result = self.postgresql_client.execute(query)

                    expect(result).to(
                        equal([
                            (1, 'item_a', 40, False, datetime.datetime(1970, 1, 1, 1, 1, 40)),
                            (2, 'item_b', 20, True, datetime.datetime(1970, 1, 1, 2, 1, 40)),
                        ]))

            with context('when counting rows'):
                with it('returns number of values'):

                    result = self.postgresql_client.execute(f"SELECT COUNT(*) FROM {TEST_TABLE}")

                    expect(result[0][0]).to(equal(2))

            with context('when selecting non-existing rows'):
                with it('returns empty list'):
                    query = f"SELECT * FROM {TEST_TABLE} WHERE size > %s;"
                    params = (50,)

                    result = self.postgresql_client.execute(query, params)

                    expect(result).to(equal([]))

            with context('when deleting a row'):
                with it('returns empty list'):
                    query = f"DELETE FROM {TEST_TABLE} WHERE active = %s;"
                    params = (False,)

                    result = self.postgresql_client.execute(query, params)

                    expect(result).to(equal([]))

            with context('when inserting a row'):
                with it('returns empty list'):
                    query = f"INSERT INTO {TEST_TABLE}(item, size, active, date) VALUES(%s, %s, %s, %s);"
                    params = ("item_c", 60, True, datetime.datetime.fromtimestamp(11000))

                    result = self.postgresql_client.execute(query, params)

                    expect(result).to(equal([]))

            with context('when updating a row'):
                with it('returns empty list'):
                    query = f'UPDATE {TEST_TABLE} SET size = size + %s WHERE {TEST_TABLE}.item = %s;'
                    params = (10, 'item_a')

                    result = self.postgresql_client.execute(query, params)

                    expect(result).to(equal([]))

        with context('unhappy path'):
            with context('when executing a query with an invalid column'):
                with it('raises exception from postgres'):
                    malformed_query = f'UPDATE {TEST_TABLE} SET size = size + %s WHERE {TEST_TABLE}.invalid_column = %s;'
                    params = (10, 'item_a')

                    def _execute_query_with_an_invalid_column():
                        self.postgresql_client.execute(malformed_query, params)

                    expect(_execute_query_with_an_invalid_column).to(
                        raise_error(psycopg2_errors.UndefinedColumn, contain('column test_table.invalid_column does not exist')))

            with context('when executing a query with an invalid param'):
                with it('raises exception from postgres'):
                    query = f'SELECT * FROM {TEST_TABLE} WHERE active = %s;'
                    invalid_params = ('invalid_param',)

                    def _execute_query_with_an_invalid_param():
                        self.postgresql_client.execute(query, invalid_params)

                    expect(_execute_query_with_an_invalid_param).to(
                        raise_error(psycopg2_errors.InvalidTextRepresentation, contain('invalid input syntax')))

            with context('when executing an empty query'):
                with it('raises exception from postgres'):
                    empty_query = ''

                    def _execute_empty_query():
                        self.postgresql_client.execute(empty_query)

                    expect(_execute_empty_query).to(
                        raise_error(psycopg2_errors.ProgrammingError, contain('can\'t execute an empty query')))

            with context('when executing a malformed query'):
                with it('raises exception from postgres'):
                    malformed_query = f"SELEC * FROM {TEST_TABLE}"

                    def _execute_malformed_query():
                        self.postgresql_client.execute(malformed_query)

                    expect(_execute_malformed_query).to(raise_error(psycopg2_errors.SyntaxError, contain('syntax error')))

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

                    expect(_execute_malformed_query).to(raise_error(psycopg2_errors.InvalidTextRepresentation))

                with it('rolls back any changes made until the failure'):

                    def _execute_malformed_query():
                        self.postgresql_client.execute_with_transactions([self.operation_1, self.failing_operation_3])

                    expect(_execute_malformed_query).to(raise_error)
                    expect(self.postgresql_client.execute(f"SELECT (size) FROM {TEST_TABLE};")).to(equal([(40,), (20,)]))
