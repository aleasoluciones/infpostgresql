import time
import os

from infcommon import logger


# make a better debugging variable
POSTGRES_DEBUG = os.getenv('POSTGRES_DEBUG', 'False') == 'True'

def _get_params_val(param_val):
    if isinstance(param_val, str):
        param_val = f"'{param_val}'"
    return str(param_val)

def _build_query(query:str, params = None):
    if params:
        if isinstance(params, dict):
            for param, param_val in params.items():
                query =  query.replace(f'%({param})s', _get_params_val(param_val))
        else:
            for param_val in params:
                query =  query.replace('%s',  _get_params_val(param_val),1)
    return query

def _print_query(query, params, end_time, start_time):
    logger.info(f"{'#'*10}POSTGRES QUERY {'#'*10}")
    logger.info(_build_query(query, params))
    logger.info(f"Query took {end_time - start_time} seconds to execute")
    logger.info('#'*35)


def _get_params_str(*args, **kwargs):
    if len(args) > 1:
        query = args[1]
        params = None
    if len(args) > 2:
        params = args[2]
    elif kwargs:
        query = kwargs.get('query')
        params = kwargs.get('params')
    return query, params

def debug_sql_call(func):
    def wrapper(*args, **kwargs):
        if not POSTGRES_DEBUG:
            return func(*args, **kwargs)

        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        query, params = _get_params_str(*args, **kwargs)
        try:
            _print_query(query, params, end_time, start_time)
        except Exception:
            logger.error('Could not print query', exc_info=True)

        return result
    return wrapper


def debug_sql_transaction_calls(func):
    def wrapper(*args, **kwargs):
        if not POSTGRES_DEBUG:
            return func(*args, **kwargs)


        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        if kwargs:
            query_params = kwargs.get('list_of_queries_with_params')
        else:
            query_params = args[1]

        try:
            logger.info(f"-----------Executing transaction query---------------------")
            for query, param in query_params:
                query, params = _get_params_str(query=query, params=param)
                _print_query(query, params, end_time, start_time)
            logger.info(f"----------------------------------------------------------------")
        except Exception:
            logger.error('Could not print query', exc_info=True)

        return result
    return wrapper
