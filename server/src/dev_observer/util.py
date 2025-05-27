import datetime
from abc import abstractmethod
from typing import Protocol


class Clock(Protocol):

    @abstractmethod
    def now(self) -> datetime.datetime:
        pass

class RealClock(Clock):
    def now(self) -> datetime.datetime:
        return datetime.datetime.now()

class MockClock(Clock):
    t: datetime.datetime = datetime.datetime.now()
    def now(self) -> datetime.datetime:
        return self.t

    def bump(self, delta: datetime.timedelta):
        self.t += delta