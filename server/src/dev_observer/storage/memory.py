from dev_observer.api.storage.local_pb2 import LocalStorageData
from dev_observer.storage.single_blob import SingleBlobStorageProvider
from dev_observer.util import Clock, RealClock


class MemoryStorageProvider(SingleBlobStorageProvider):
    _data: LocalStorageData = LocalStorageData()

    def __init__(self, clock: Clock = RealClock()):
        super().__init__(clock)

    def _get(self) -> LocalStorageData:
        return self._data

    def _store(self, data: LocalStorageData):
        self._data = data
