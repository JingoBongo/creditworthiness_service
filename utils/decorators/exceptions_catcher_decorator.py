import __init__
from utils import logger_utils as log


def catch_exceptions(*exc_types):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                if isinstance(e, exc_types) or not exc_types:
                    # log.exception(f"Exception caught: {type(e).__name__}: {str(e)}")
                    print(f"Exception caught: {type(e).__name__}: {str(e)}")
                else:
                    raise

        return wrapper

    return decorator
