# infpostgresql

Wrapper for the [psycopg2](https://www.psycopg.org) library using Python 3.7.

## Development

### Setup

Create a virtual environment, install dependencies and load environment variables.

```python
mkvirtualenv infpostgresql -p $(which python3.7)
dev/setup_venv.sh
source dev/env_develop
```

Run a PostgreSQL Docker container.

```python
dev/start_local_dependencies.sh
```

### Running tests, linter & formatter and configure git hooks

Note that project uses Alea's [pydevlib](https://github.com/aleasoluciones/pydevlib), so take a look at its README to see the available commands.

## Internals

In the `execute()` method of the `PostgresClient` class, we're enclosing the `cursor.fetchall()` call in a try-except block. The reason is that that method only makes sense if the database returns data. Otherwise it will throw a `ProgrammingError` exception, which we intercept. Any other exception is allowed to bubble up, so we can still know what's wrong from the outside.

This design is for the sake of homogeneity, so we can aways use the `execute()` method the same, no matter what kind of SQL statement is being executed.

## infpostgresql client API

Below is described the public API that this library provides.

### \_\_init\_\_()

The client must be initialized with a database URI.

> postgres_client = **PostgresClient**(*database_uri*)

### execute()

Executes a SQL query and returns the result. Passing parameters is possible by using `%s` placeholders in the SQL query, and passing a sequence of values as the second argument of the function.

> postgresql_client.**execute**(*query*, *args*)

➡️ Parameters

- **query**: `str`
- **args** (optional): `tuple<any>`. Defaults to `None`.

⬅️ Returns a list of tuples, each containing a row of results.

`list<tuple<any>>`

💥 Throws any Postgres error converted to CamelCase (available [here](https://www.postgresql.org/docs/12/errcodes-appendix.html), some examples in the [integration tests](integration_specs/postgresql_spec.py)).

#### Usage example

```python
from infpostgresql.client import PostgresClient

postgres_client = PostgresClient('postgres://username:password@host:port/databasename')

query = 'SELECT (name, surname, age) FROM users WHERE age < %s AND active = %s;'
params = (30, True, )

result = postgres_client.execute(query, params)

# [('Ann', 'White', 18, ), ('Axel', 'Schwarz', 21, ), ('Camille', 'Rouge', '27', )]
```

### execute_with_transactions()

Executes multiple SQL queries. Each query can be sent along with their parameters. If any of them fails, the whole process is reversed to ensure the integrity of the transaction.

> postgresql_client.**execute_with_transactions**(*list_of_queries_with_args*)

➡️ Parameters

- **list_of_queries_with_args**: `list<tuple<str, tuple<any>>>`

⬅️ Returns nothing

`None`

💥 Throws any Postgres error converted to CamelCase (available [here](https://www.postgresql.org/docs/12/errcodes-appendix.html), some examples in the [integration tests](integration_specs/postgresql_spec.py)).

#### Usage example

```python
from infpostgresql.client import PostgresClient

postgres_client = PostgresClient('postgres://username:password@host:port/databasename')

query_1 = 'UPDATE bank_account SET balance = balance - %s WHERE name = %s;'
params_1 = (100, 'Jack', )
operation_1 = (query_1, params_1, )

query_2 = 'INSERT INTO bank_account(name, balance) VALUES (%s, %s);'
params_2 = ('Kate', 100, )
operation_2 = (query_2, params_2, )

result = postgres_client.execute_with_transactions([operation_1, operation_2])
```
