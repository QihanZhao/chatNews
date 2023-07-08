import asyncio
import time


def async_retry(max_retries=3, initial_delay=1, multiplier=2):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:

                    print(f"Retry {retries + 1}/{max_retries} - {func.__name__}: {e} , parameters: {args}, {kwargs}")
                    await asyncio.sleep(delay)
                    delay *= multiplier
                    retries += 1
                    if retries == max_retries:
                        raise e


        return wrapper

    return decorator

def retry(max_retries=3, initial_delay=1, multiplier=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:

                    print(f"Retry {retries + 1}/{max_retries} - {func.__name__}: {e} , parameters: {args}, {kwargs}")
                    time.sleep(delay)
                    delay *= multiplier
                    retries += 1
                    if retries == max_retries:
                        raise e
        return wrapper
    return decorator