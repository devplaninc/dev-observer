from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.api.types.config_pb2 import GlobalConfig
from dev_observer.flatten.flatten import flatten_repository, FlattenResult
from dev_observer.observations.provider import ObservationsProvider
from dev_observer.processors.flattening import FlatteningProcessor
from dev_observer.prompts.provider import PromptsProvider
from dev_observer.repository.provider import GitRepositoryProvider
from dev_observer.repository.types import ObservedRepo
from dev_observer.tokenizer.provider import TokenizerProvider


class ReposProcessor(FlatteningProcessor[ObservedRepo]):
    repository: GitRepositoryProvider
    tokenizer: TokenizerProvider

    def __init__(
            self,
            analysis: AnalysisProvider,
            repository: GitRepositoryProvider,
            prompts: PromptsProvider,
            observations: ObservationsProvider,
            tokenizer: TokenizerProvider,
    ):
        super().__init__(analysis, prompts, observations)
        self.repository = repository
        self.tokenizer = tokenizer

    async def get_flatten(self, repo: ObservedRepo, config: GlobalConfig) -> FlattenResult:
        res = await flatten_repository(repo, self.repository, self.tokenizer, config)
        return res.flatten_result
