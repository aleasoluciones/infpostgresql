from mamba import description, context, it
from expects import expect, equal

from infpostgresql.client import PostgresClient

with description('PostgresqlClient specs') as self:
    with context('setting db_uri'):
        with it('set db_uri'):
            self.postgres_client = PostgresClient(db_uri='updated_db_uri')

            # pylint: disable=protected-access
            expect(self.postgres_client._db_uri).to(equal('updated_db_uri'))
