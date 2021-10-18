from infcommon.factory import Factory

from infpostgresql.async_client.client import AsyncPostgresClient


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
