import os
import psycopg2.extras

from postgresql_wrapper.client import PostgresClient


class Factory(object):
    _instances = {}

    @classmethod
    def instance(cls, id, create_instance):
        if id not in cls._instances:
            cls._instances[id] = create_instance()

        return cls._instances[id]


def postgres_client_from_connection_parameters(user=None, password=None, host=None, port=None, db_name=None, use_dict_cursor=None):
    connection_uri = 'postgresql://{user}:{password}@{host}:{port}/{db_name}'.format(user=user, password=password, host=host, port=port, db_name=db_name)
    return _postgres_client(connection_uri, use_dict_cursor)


def _postgres_client(connection_uri=None, use_dict_cursor=None):
    cursor_factory = _cursor_factory(use_dict_cursor)
    instance_id = "postgres_client_{}_{}".format(connection_uri, use_dict_cursor)
    return Factory.instance(instance_id,
                            lambda: PostgresClient(connection_uri, cursor_factory=cursor_factory)
                           )


def _cursor_factory(use_dict_cursor=None):
    if use_dict_cursor:
        return psycopg2.extras.DictCursor
    return None
