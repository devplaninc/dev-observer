import datetime
from abc import abstractmethod
from typing import Protocol, TypeVar

from google.protobuf import json_format
from google.protobuf.message import Message


class Clock(Protocol):
    @abstractmethod
    def now(self) -> datetime.datetime:
        pass


class RealClock(Clock):
    def now(self) -> datetime.datetime:
        return datetime.datetime.now(tz=datetime.timezone.utc)


class MockClock(Clock):
    t: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)

    def now(self) -> datetime.datetime:
        return self.t

    def bump(self, delta: datetime.timedelta):
        self.t += delta


M = TypeVar("M", bound=Message)


def pb_to_json(pb: M, indent=0) -> str:
    return json_format.MessageToJson(pb, indent=indent, sort_keys=True)


def parse_dict_pb(msg: dict, m: M) -> M:
    return json_format.ParseDict(msg, m, ignore_unknown_fields=True)
