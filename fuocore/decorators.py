from functools import wraps
import logging
import time


logger = logging.getLogger(__name__)


def log_exectime(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t = time.process_time()
        result = func(*args, **kwargs)
        elapsed_time = time.process_time() - t
        logger.info('function %s executed time: %f ms'
                    % (func.__name__, elapsed_time * 1000))
        return result
    return wrapper
