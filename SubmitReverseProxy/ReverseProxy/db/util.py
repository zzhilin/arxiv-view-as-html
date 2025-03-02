from typing import Callable
from functools import wraps
import time

from ..exceptions import DBConnectionError

def database_retry (retries: int):

    def decorator (func: Callable) -> Callable:

        @wraps(func)
        def wrapped (*args, **kwargs):
            for _ in range(retries):
                try:
                    return func(*args, **kwargs)
                except DBConnectionError:
                    time.sleep(3)
            raise DBConnectionError
        
        return wrapped
    
    return decorator
