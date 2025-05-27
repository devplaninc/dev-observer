import os.path

from google.protobuf import json_format

from dev_observer.api.storage.local_pb2 import LocalStorageData
from dev_observer.storage.single_blob import SingleBlobStorageProvider
from dev_observer.util import Clock, RealClock


class LocalStorageProvider(SingleBlobStorageProvider):
    _dir: str

    def __init__(self, root_dir: str, clock: Clock = RealClock()):
        super().__init__(clock)
        os.makedirs(root_dir, exist_ok=True)
        self._dir = root_dir

    def _get_path(self) -> str:
        return os.path.join(self._dir, "full_data.json")

    def _get(self) -> LocalStorageData:
        path = self._get_path()
        if not os.path.exists(path):
            return LocalStorageData()
        with open(path, 'r') as in_file:
            data = in_file.read()
            res = LocalStorageData()
            return json_format.Parse(data, res, ignore_unknown_fields=True)

    def _store(self, data: LocalStorageData):
        with open(self._get_path(), 'w') as out_file:
            out_file.write(json_format.MessageToJson(data))
