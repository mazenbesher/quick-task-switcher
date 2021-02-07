import time
from typing import Optional


class StopWatch():
    def __init__(self, name: Optional[str] = None):
        self.name = name
        self.running = False
        self.elapsed = 0
        self.start_time = None
        self.pause_time = None

    def start(self):
        if self.running:
            raise ValueError('Watch is already running!')
        self._add_elapsed()
        self.start_time = time.time()
        self.running = True
        self.pause_time = None

    def pause(self):
        if not self.running:
            raise ValueError('Watch is not running!')
        self.pause_time = time.time()
        self._add_elapsed()
        self.running = False
        self.start_time = None

    def _add_elapsed(self):
        """start or pause time are going to be overwritten, thus add any elapsed time"""
        if self.start_time is not None and self.pause_time is not None:
            assert self.pause_time > self.start_time
            self.elapsed += self.pause_time - self.start_time

    def get_elapsed(self) -> float:
        """return current time in seconds"""
        if not self.running:
            return self.elapsed
        return self.elapsed + (time.time() - self.start_time)

    def get_elapsed_formatted(self) -> str:
        hours, remainder = divmod(self.get_elapsed(), 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))


if __name__ == '__main__':
    test1 = True
    test2 = False

    if test1:
        s1 = StopWatch('s1')
        s2 = StopWatch('s2')

        s1.start()
        print(s1.get_elapsed(), s2.get_elapsed())  # s1: 0, s2: 0

        time.sleep(1)
        s2.start()
        print(s1.get_elapsed(), s2.get_elapsed())  # s1: 1, s2: 0

        time.sleep(1)
        s1.pause()
        print(s1.get_elapsed(), s2.get_elapsed())  # s1: 2, s2: 1

        time.sleep(1)
        s2.pause()
        s1.start()
        print(s1.get_elapsed(), s2.get_elapsed())  # s1: 2, s2: 2

        time.sleep(1)
        print(s1.get_elapsed(), s2.get_elapsed())  # s1: 3, s2: 2

    if test2:
        s3 = StopWatch('s3')
        s3.start()
        time.sleep(0.5)
        print(s3.get_elapsed())

        s3.pause()  # 0.5
        time.sleep(0.5)
        print(s3.get_elapsed())

        s3.start()  # 0.5
        time.sleep(1.5)
        print(s3.get_elapsed())  # 2
