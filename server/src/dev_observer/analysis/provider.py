import dataclasses
from abc import abstractmethod
from typing import Protocol, Optional

from dev_observer.prompts.provider import FormattedPrompt


@dataclasses.dataclass
class AnalysisResult:
    analysis: str


class AnalysisProvider(Protocol):
    @abstractmethod
    async def analyze(self, prompt: FormattedPrompt, session_id: Optional[str] = None) -> AnalysisResult:
        ...
