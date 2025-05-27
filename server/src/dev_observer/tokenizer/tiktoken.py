from typing import List

import tiktoken
from tiktoken import Encoding

from dev_observer.tokenizer.provider import TokenizerProvider


class TiktokenTokenizerProvider(TokenizerProvider):
    _encoding: Encoding

    def __init__(self, encoding: str):
        self._encoding = tiktoken.get_encoding(encoding)

    def encode(self, content: str) -> List[int]:
        return self._encoding.encode(content)

    def decode(self, tokens: List[int]) -> str:
        return self._encoding.decode(tokens)
