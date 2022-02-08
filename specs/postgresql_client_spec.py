from mamba import description, context, it, before
from expects import expect, equal, be_none

from infpostgresql.client import PostgresClient
from infpostgresql.factory import postgres_client_from_connection_parameters

# pylint: disable=protected-access
with description('PostgresqlClient specs') as self:
    with context('setting db_uri without cursor factory'):
        with before.each:
            self.postgres_client = PostgresClient(db_uri='a_db_uri')

        with it('sets db_uri'):
            db_uri = self.postgres_client._db_uri
            expect(db_uri).to(equal('a_db_uri'))

        with it('does not set a cursor factory'):
            cursor_factory = self.postgres_client._cursor_factory
            expect(cursor_factory).to(be_none)

    with context('setting factory db_uri with cursor factory'):
        with before.each:
            self.postgres_client = postgres_client_from_connection_parameters(
                user='a_user',
                password='a_password',
                host='a_host',
                port='a_port',
                db_name='a_db_name',
                use_dict_cursor=True
            )

        with it('sets db_uri'):
            db_uri = self.postgres_client._db_uri
            expect(db_uri).to(equal('postgresql://a_user:a_password@a_host:a_port/a_db_name'))

        with it('sets dict cursor factory'):
            cursor_factory_name = self.postgres_client._cursor_factory.__name__
            expect(cursor_factory_name).to(equal('DictCursor'))

