from dev_observer.api.types import observations_pb2 as _observations_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetObservationsResponse(_message.Message):
    __slots__ = ("keys",)
    KEYS_FIELD_NUMBER: _ClassVar[int]
    keys: _containers.RepeatedCompositeFieldContainer[_observations_pb2.ObservationKey]
    def __init__(self, keys: _Optional[_Iterable[_Union[_observations_pb2.ObservationKey, _Mapping]]] = ...) -> None: ...

class GetObservationResponse(_message.Message):
    __slots__ = ("observation",)
    OBSERVATION_FIELD_NUMBER: _ClassVar[int]
    observation: _observations_pb2.Observation
    def __init__(self, observation: _Optional[_Union[_observations_pb2.Observation, _Mapping]] = ...) -> None: ...
