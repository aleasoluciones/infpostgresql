import psycopg2.extras

from infcommon.factory import Factory

from infpostgresql.client import PostgresClient, AsyncPostgresClient


def postgres_client_from_connection_parameters(user=None,
                                               password=None,
                                               host=None,
                                               port=None,
                                               db_name=None,
                                               use_dict_cursor=None):
    connection_uri = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
    return _postgres_client(connection_uri, use_dict_cursor)


def _postgres_client(connection_uri=None, use_dict_cursor=None):
    cursor_factory = _cursor_factory(use_dict_cursor)
    instance_id = f'postgres_client_{connection_uri}_{use_dict_cursor}'
    return Factory.instance(instance_id, lambda: PostgresClient(connection_uri, cursor_factory=cursor_factory))


def _cursor_factory(use_dict_cursor=None):
    if use_dict_cursor:
        return psycopg2.extras.DictCursor
    return None


def async_postgres_client_from_connection_parameters(user=None, password=None, host=None, port=None, db_name=None):
    db_connection_dto = {
        'username': user,
        'password': password,
        'host': host,
        'port': port,
        'database': db_name,
    }
    dto_string = "_".join([str(value) for _, value in db_connection_dto.items()])
    instance_id = f'postgres_client_{dto_string}'
    return Factory.instance(instance_id, lambda: AsyncPostgresClient(db_connection_dto))
