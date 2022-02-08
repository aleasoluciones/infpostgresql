import psycopg

from infcommon.factory import Factory

from infpostgresql.client import PostgresClient


def postgres_client_from_connection_parameters(user=None,
                                               password=None,
                                               host=None,
                                               port=None,
                                               db_name=None,
                                               use_dict_cursor=False):
    connection_uri = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
    cursor_factory = _cursor_factory(use_dict_cursor)
    return Factory.instance(
        f'postgres_client_{connection_uri}_{use_dict_cursor}',
        lambda: PostgresClient(connection_uri, cursor_factory=cursor_factory)
    )


def postgres_client_from_connection_uri(connection_uri=None,
                                        use_dict_cursor=False):
    cursor_factory = _cursor_factory(use_dict_cursor)
    return Factory.instance(
        f'postgres_client_{connection_uri}_{use_dict_cursor}',
        lambda: PostgresClient(connection_uri, cursor_factory=cursor_factory)
    )


def _cursor_factory(use_dict_cursor=False):
    if use_dict_cursor:
        return psycopg.rows.dict_row
    return None
