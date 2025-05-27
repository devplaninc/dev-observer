import abc
import dataclasses
from abc import abstractmethod
from typing import TypeVar, Generic, List

from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.api.devplan.observer.types.observations_pb2 import Observation, ObservationKey
from dev_observer.flatten.flatten import FlattenResult
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.tokenized import TokenizedAnalyzer
from dev_observer.prompts.provider import PromptsProvider

E = TypeVar("E")


@dataclasses.dataclass
class ObservationRequest:
    prompt_prefix: str
    key: ObservationKey


class FlatteningProcessor(abc.ABC, Generic[E]):
    analysis: AnalysisProvider
    prompts: PromptsProvider
    observations: ObservationsProvider

    def __init__(
            self,
            analysis: AnalysisProvider,
            prompts: PromptsProvider,
            observations: ObservationsProvider,
    ):
        self.analysis = analysis
        self.prompts = prompts
        self.observations = observations

    async def process(self, entity: E, requests: List[ObservationRequest]):
        res = await self.get_flatten(entity)
        for request in requests:
            prompts_prefix = request.prompt_prefix
            key = request.key
            analyzer = TokenizedAnalyzer(prompts_prefix=prompts_prefix, analysis=self.analysis, prompts=self.prompts)
            content = await analyzer.analyze_flatten(res)
            await self.observations.store(Observation(key=key, content=content.encode('utf-8')))

    @abstractmethod
    async def get_flatten(self, entity: E) -> FlattenResult:
        pass
