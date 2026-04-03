import time
from functools import wraps


def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"'{func.__name__}' took {execution_time:.4f} seconds to complete")  # noqa: T201
        return result

    return wrapper
