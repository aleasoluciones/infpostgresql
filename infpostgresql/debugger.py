import time
import os
import logging
import re

# make a better debugging variable
POSTGRE_DEBUG = os.getenv('POSTGRES_DEBUG', 'False') == 'True'

def get_params_val(param_val):
    if isinstance(param_val, str):
        param_val = f"'{param_val}'"
    return str(param_val)

def build_query(query:str, params: dict|tuple|None = None):
    if params:
        if isinstance(params, dict):
            for param, param_val in params.items():
                query =  query.replace(f'%({param})s', get_params_val(param_val))
        else:
            for param_val in params:
                query =  query.replace('%s',  get_params_val(param_val),1)
    return query
    
def print_query(query, params, end_time, start_time):
    logging.info(f"{'#'*10}POSTGRES QUERY {'#'*10}")
    logging.info(build_query(query, params))
    logging.info(f"Query took {end_time - start_time} seconds to execute")
    logging.info('#'*35)
    
    
    
def debug_sql_call(func):
    def wrapper(*args, **kwargs):
        if not POSTGRE_DEBUG:
            return func(*args, **kwargs)    
        
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        if len(args) > 1:
            query = args[1]
            params = None
        if len(args) > 2:
            params = args[2]
        elif kwargs:
            query = kwargs.get('query')
            params = kwargs.get('params')
        try:
            print_query(query, params, end_time, start_time)
        except Exception:
            logging.error('Could not print query', exc_info=True)
            
        return result
    return wrapper