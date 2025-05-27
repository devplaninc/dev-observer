from abc import abstractmethod
from typing import Protocol, List


class TokenizerProvider(Protocol):

    @abstractmethod
    def encode(self, content: str) -> List[int]:
        ...

    @abstractmethod
    def decode(self, tokens: List[int]) -> str:
        ...