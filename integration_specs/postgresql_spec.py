from mamba import description, context, it
from expects import expect, be, have_len, be_above, equal

import os
from infpostgresql import client


TEST_TABLE = 'local'
LOCAL_DB_URI='postgres://user:password@localhost:5439/local'


with description('PostgresClientTest'):
    with before.each:
        self.postgresql_client = client.PostgresClient(LOCAL_DB_URI)

        sql_query = "DROP TABLE IF EXISTS prueba".format(TEST_TABLE)
        self.postgresql_client.execute(sql_query)

    with context('creating a table'):
        with it('creates'):
            sql_query = "CREATE TABLE prueba (value varchar(10))".format(TEST_TABLE)
            result = self.postgresql_client.execute(sql_query)

            expect(result).to(equal(list()))

    with context('making a query with results'):
        with it('returns it'):

                sql_query = "SELECT * FROM user"

                result = self.postgresql_client.execute(sql_query, ['root'])


                expect(result).to(have_len(be_above(0)))



    with context('making a query with no results'):
        with it('returns empty'):
            sql_query = "SELECT * FROM user WHERE User=%s"

            result = self.postgresql_client.execute(sql_query, ['non-existing-user'])


            expect(result).to(have_len(be(0)))

    with context('inserting value into table'):
        with it('returns inserted primary key id'):
            self.postgresql_client.execute("CREATE TABLE prueba (id SERIAL , value varchar(10), primary key (id))".format(TEST_TABLE))
            sql_query = "SELECT * FROM prueba"
            self.postgresql_client.execute("INSERT INTO prueba(value) VALUES(%s)".format(TEST_TABLE), ("foo",))

            result = self.postgresql_client.execute(sql_query, ['root'])

            print("Result: "+str(len(result)) )
            expect(result[0][0] ).to(equal(1))


