from time import time


class SimpleTimer:
    def __enter__(self):
        self.start_time = time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f'{time() - self.start_time}s')
