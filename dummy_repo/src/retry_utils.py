"""Dummy retry utility - exercises decorators, recursion, and nested
control flow for knowledge graph testing."""

import time
import functools


def retry(max_attempts=3, backoff_seconds=1, backoff_multiplier=2):
    """Decorator that retries a function on exception, with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            delay = backoff_seconds
            last_error = None
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    attempt += 1
                    if attempt < max_attempts:
                        time.sleep(delay)
                        delay *= backoff_multiplier
            raise last_error
        return wrapper
    return decorator


@retry(max_attempts=3, backoff_seconds=0.1)
def fetch_with_retry(client, url):
    """Fetch a URL using the given client, retrying on failure."""
    response = client.get(url)
    if response.status_code >= 500:
        raise ConnectionError(f"Server error {response.status_code} for {url}")
    return response


def exponential_backoff_delay(attempt, base_delay=1, multiplier=2, max_delay=60):
    """Compute the delay for a given retry attempt number."""
    delay = base_delay * (multiplier ** attempt)
    return min(delay, max_delay)


def factorial(n):
    """Compute n! recursively -- simple recursion example for KG testing."""
    if n < 0:
        raise ValueError("factorial is undefined for negative numbers")
    if n in (0, 1):
        return 1
    return n * factorial(n - 1)


def fibonacci(n, memo=None):
    """Compute the nth Fibonacci number using memoized recursion."""
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    result = fibonacci(n - 1, memo) + fibonacci(n - 2, memo)
    memo[n] = result
    return result


def batch_retry_calls(items, call_fn, max_attempts=3):
    """Apply call_fn to each item, retrying failures, and collect results/errors."""
    results = []
    failures = []
    for item in items:
        attempt = 0
        succeeded = False
        while attempt < max_attempts and not succeeded:
            try:
                result = call_fn(item)
                results.append(result)
                succeeded = True
            except Exception as e:
                attempt += 1
                if attempt >= max_attempts:
                    failures.append({"item": item, "error": str(e)})
    return results, failures
