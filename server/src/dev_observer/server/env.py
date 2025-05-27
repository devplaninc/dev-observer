import dataclasses
from typing import Optional

from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.repos import ReposProcessor


@dataclasses.dataclass
class ServerEnv:
    observations: ObservationsProvider
    repos_processor: ReposProcessor
