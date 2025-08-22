import time
import functools
from openai import InternalServerError, RateLimitError
import requests


def retry_request(retries=5, backoff_factor=2, exceptions=None):
    """
    Decorator to retry OpenAI API calls on errors with exponential backoff.

    Parameters:
        retries (int): Max attempts
        backoff_factor (int): Exponential backoff factor (2 => 1s, 2s, 4s...)
        exceptions (tuple): Exception types to catch (defaults include InternalServerError, RateLimitError, network errors)
    """
    if exceptions is None:
        exceptions = (InternalServerError, RateLimitError,
                      requests.exceptions.RequestException,
                      TimeoutError, ConnectionError)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if i == retries - 1:
                        raise  # re-raise after last attempt
                    wait = backoff_factor ** i
                    print(f"⚠️ {type(e).__name__}: {e}. Retrying in {wait}s...")
                    time.sleep(wait)
        return wrapper
    return decorator
