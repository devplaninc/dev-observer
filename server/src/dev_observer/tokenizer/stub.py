from typing import List

from dev_observer.tokenizer.provider import TokenizerProvider


class StubTokenizerProvider(TokenizerProvider):
    def encode(self, content: str) -> List[int]:
        result: List[int] = []
        for c in content:
            res: int = 0
            for b in c.encode("utf-8"):
                res = (res << 8) + int(b)
            result.append(res)
        return result

    def decode(self, tokens: List[int]) -> str:
        result: str = ""
        for c in tokens:
            tb: List[int] = []
            tc = c
            while tc > 0:
                tb.append(tc % 256)
                tc = tc >> 8
            tb.reverse()
            result += str(bytes(tb))
        return result
