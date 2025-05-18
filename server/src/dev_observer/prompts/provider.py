import dataclasses
from abc import abstractmethod
from typing import Protocol, Optional, Dict

from langfuse.model import ChatPromptClient

from dev_observer.api.devplan.observer.types.ai_pb2 import ModelConfig, SystemMessage, UserMessage


@dataclasses.dataclass
class FormattedPrompt:
    system: Optional[SystemMessage]
    user: Optional[UserMessage]
    model_config: Optional[ModelConfig] = None
    langfuse_prompt: Optional[ChatPromptClient] = None


class PromptsProvider(Protocol):
    @abstractmethod
    def get_formatted(self, name: str, params: Optional[Dict[str, str]] = None) -> FormattedPrompt:
        ...

