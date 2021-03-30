import os
import psycopg2.extras

from infpostgresql.client import PostgresClient

from infcommon.factory import Factory


def postgres_client_from_connection_parameters(user=None, password=None, host=None, port=None, db_name=None, use_dict_cursor=None):
    connection_uri = 'postgresql://{user}:{password}@{host}:{port}/{db_name}'.format(user=user, password=password, host=host, port=port, db_name=db_name)
    return _postgres_client(connection_uri, use_dict_cursor)


def _postgres_client(connection_uri=None, use_dict_cursor=None):
    cursor_factory = _cursor_factory(use_dict_cursor)
    instance_id = 'postgres_client_{connection_uri}_{use_dict_cursor}'.format(connection_uri=connection_uri, use_dict_cursor=use_dict_cursor)
    return Factory.instance(instance_id,
                            lambda: PostgresClient(connection_uri, cursor_factory=cursor_factory)
                           )


def _cursor_factory(use_dict_cursor=None):
    if use_dict_cursor:
        return psycopg2.extras.DictCursor
    return None
