import dataclasses
from abc import abstractmethod
from typing import Protocol, Optional, Dict

from langfuse.model import ChatPromptClient

from dev_observer.api.types.ai_pb2 import PromptConfig, SystemMessage, UserMessage


@dataclasses.dataclass
class FormattedPrompt:
    config: PromptConfig
    system: Optional[SystemMessage]
    user: Optional[UserMessage]
    langfuse_prompt: Optional[ChatPromptClient] = None


class PromptsProvider(Protocol):
    @abstractmethod
    async def get_formatted(self, name: str, params: Optional[Dict[str, str]] = None) -> FormattedPrompt:
        ...
