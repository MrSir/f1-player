import time
from functools import wraps

def timeit(func):
    """
    Decorator to measure the execution time of a function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # Record the start time
        result = func(*args, **kwargs)    # Execute the function
        end_time = time.perf_counter()    # Record the end time
        execution_time = end_time - start_time
        print(f"'{func.__name__}' took {execution_time:.4f} seconds to complete")
        return result
    return wrapper