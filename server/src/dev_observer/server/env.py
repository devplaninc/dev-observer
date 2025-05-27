import dataclasses

from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.repos import ReposProcessor
from dev_observer.storage.provider import StorageProvider


@dataclasses.dataclass
class ServerEnv:
    observations: ObservationsProvider
    storage: StorageProvider
    repos_processor: ReposProcessor
