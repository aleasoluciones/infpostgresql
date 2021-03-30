from mamba import description, context, it
from expects import expect, equal


from infpostgresql.client import PostgresClient


with description('PostgresqlClient specs'):
    with context('setting db_uri'):
        with it('set db_uri'):
            self.sut = PostgresClient(db_uri='updated_db_uri')

            expect(self.sut._db_uri).to(equal('updated_db_uri'))
