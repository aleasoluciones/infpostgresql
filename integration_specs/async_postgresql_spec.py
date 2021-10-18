from mamba import description, context, before, it
from expects import expect, equal, contain, raise_error

import datetime
import os

from asyncpg import exceptions as asyncpg_exceptions
from infpostgresql.async_client.client import AsyncPostgresClient

POSTGRES_HOSTNAME = os.getenv('POSTGRES_HOSTNAME')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')

POSTGRES_DB_CONNECTION_CONFIG = {
    'username': POSTGRES_USER,
    'password': POSTGRES_PASSWORD,
    'host': POSTGRES_HOSTNAME,
    'port': POSTGRES_PORT,
    'database': POSTGRES_DB,
}

TEST_TABLE = 'test_table'

with description('AsyncPostgresClient Specs') as self:
    with before.each:
        self.postgresql_client = AsyncPostgresClient(POSTGRES_DB_CONNECTION_CONFIG)
        self.db_connection = self.postgresql_client.get_db_connection()
        self.postgresql_client.execute(self.db_connection.schema(f'TABLE IF EXISTS {TEST_TABLE}').drop())
        self.postgresql_client.execute(self.db_connection.schema(f'TABLE IF EXISTS {TEST_TABLE}').drop())
        self.postgresql_client.execute(
            self.db_connection.schema(f'TABLE {TEST_TABLE}').create('id SERIAL PRIMARY KEY', 'item VARCHAR(10)', 'size INTEGER',
                                                                    'active BOOLEAN', 'created_at TIMESTAMP'))
        self.postgresql_client.execute(
            self.db_connection.table(TEST_TABLE).insert(
                {
                    'item': 'item_a',
                    'size': 40,
                    'active': 'false',
                    'created_at': datetime.datetime.fromtimestamp(100)
                },
                {
                    'item': 'item_b',
                    'size': 20,
                    'active': 'true',
                    'created_at': datetime.datetime.fromtimestamp(3700)
                },
            ))

    with context('FEATURE: execute'):
        with context('happy path'):
            with context('when selecting all rows'):
                with it('returns a list containing all values'):
                    query = self.db_connection.table(f'{TEST_TABLE}').select()

                    result = self.postgresql_client.execute(query)

                    expect(result).to(
                        equal([
                            (1, 'item_a', 40, False, datetime.datetime.fromtimestamp(100)),
                            (2, 'item_b', 20, True, datetime.datetime.fromtimestamp(3700)),
                        ]))

            with context('when selecting non-existing rows'):
                with it('returns empty list'):
                    query = self.db_connection.table(f'{TEST_TABLE}').select().where('size', '>', '50')

                    result = self.postgresql_client.execute(query)

                    expect(result).to(equal([]))

            with context('when deleting a row'):
                with it('returns empty list'):
                    query = self.db_connection.table(f'{TEST_TABLE}').where('active', '=', 'false').delete()

                    result = self.postgresql_client.execute(query)

                    expect(result).to(equal([]))

            with context('when inserting a row'):
                with it('returns empty list'):
                    query = self.db_connection.table(f'{TEST_TABLE}').insert({
                        'item': 'item_c',
                        'size': 60,
                        'active': 'false',
                        'created_at': datetime.datetime.fromtimestamp(11000)
                    })

                    result = self.postgresql_client.execute(query)

                    expect(result).to(equal([]))

            with context('when updating a row'):
                with it('returns empty list'):
                    query = self.db_connection.table(f'{TEST_TABLE}').where(f'{TEST_TABLE}.item', '=',
                                                                            'item_a').update('size = size + 10')

                    result = self.postgresql_client.execute(query)

                    expect(result).to(equal([]))

        with context('unhappy path'):
            with context('when executing a query with an invalid column'):
                with it('raises exception from postgres'):
                    query = self.db_connection.table(f'{TEST_TABLE}').where(f'{TEST_TABLE}.invalid_column', '=',
                                                                            'item_a').update('size = size + 10')

                    def _execute_query_with_an_invalid_column():
                        self.postgresql_client.execute(query)

                    expect(_execute_query_with_an_invalid_column).to(
                        raise_error(asyncpg_exceptions.UndefinedColumnError,
                                    contain('column test_table.invalid_column does not exist')))

            with context('when executing a query with an invalid param'):
                with it('raises exception from postgres'):
                    query = self.db_connection.table(f'{TEST_TABLE}').select().where('active', '=', 'invalid_param')

                    def _execute_query_with_an_invalid_param():
                        self.postgresql_client.execute(query)

                    expect(_execute_query_with_an_invalid_param).to(
                        raise_error(asyncpg_exceptions.InvalidTextRepresentationError, contain('invalid input syntax')))

    with context('FEATURE: raw execute'):
        with context('happy path'):
            with context('when counting rows'):
                with it('returns number of values'):
                    query = f"SELECT COUNT(*) FROM {TEST_TABLE}"

                    result = self.postgresql_client.raw_execute(query)

                    expect(result[0][0]).to(equal(2))
