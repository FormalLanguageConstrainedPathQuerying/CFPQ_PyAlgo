import signal
from contextlib import contextmanager


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):
    if seconds is None:
        yield
    else:
        def signal_handler(signum, frame):
            raise TimeoutException(f"Timed out! Time limit was {seconds} seconds.")

        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
