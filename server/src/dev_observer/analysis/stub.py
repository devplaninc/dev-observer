from typing import Optional

from dev_observer.analysis.provider import AnalysisProvider, AnalysisResult
from dev_observer.prompts.provider import FormattedPrompt


class StubAnalysisProvider(AnalysisProvider):
    async def analyze(self, prompt: FormattedPrompt, session_id: Optional[str] = None) -> AnalysisResult:
        analysis = f'''### Stub result:
 
  user len: {len(prompt.user.text)}
system len: {len(prompt.system.text)}
session id: {session_id}
'''
        return AnalysisResult(analysis=analysis)