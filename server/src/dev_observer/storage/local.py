import os.path

from google.protobuf import json_format

from dev_observer.api.storage.local_pb2 import LocalStorageData
from dev_observer.storage.single_blob import SingleBlobStorageProvider


class LocalStorageProvider(SingleBlobStorageProvider):
    _dir: str

    def __init__(self, root_dir: str):
        self._dir = root_dir

    def _get_path(self) -> str:
        return os.path.join(self._dir, "full_data.json")

    def _get(self) -> LocalStorageData:
        with open(self._get_path(), 'r') as in_file:
            data = in_file.read()
            res = LocalStorageData()
            return json_format.Parse(data, res, ignore_unknown_fields=True)

    def _store(self, data: LocalStorageData):
        with open(self._get_path(), 'w') as out_file:
            out_file.write(json_format.MessageToJson(data))
