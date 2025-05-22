from typing import List

from dev_observer.analysis.provider import AnalysisProvider
from dev_observer.flatten.flatten import flatten_repository
from dev_observer.prompts.provider import PromptsProvider
from dev_observer.repository.provider import GitRepositoryProvider


class Processor:
    analysis: AnalysisProvider
    repository: GitRepositoryProvider
    prompts: PromptsProvider

    def __init__(
            self,
            analysis: AnalysisProvider,
            repository: GitRepositoryProvider,
            prompts: PromptsProvider,
    ):
        self.analysis = analysis
        self.repository = repository
        self.prompts = prompts

    async def process(self, prompts_prefix: str, repo_url: str) -> str:
        flatten_result = flatten_repository(repo_url, self.repository)
        if len(flatten_result.file_paths) > 0:
            return await self._analyze_tokenized(prompts_prefix, flatten_result.file_paths)
        else:
            return await self._analyze_file(flatten_result.full_file_path, f"{prompts_prefix}_analyze_full")

    async def _analyze_tokenized(self, prompts_prefix: str, paths: List[str]) -> str:
        summaries: List[str] = []
        for p in paths:
            s = await self._analyze_file(p, f"{prompts_prefix}_analyze_chunk")
            summaries.append(s)

        summary = "\n\n".join(summaries)
        prompt = await self.prompts.get_formatted(f"{prompts_prefix}_analyze_combined_chunks", {
            "content": summary,
        })
        result = await self.analysis.analyze(prompt)
        return result.analysis

    async def _analyze_file(self, path: str, prompt_name: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        prompt = await self.prompts.get_formatted(prompt_name, {
            "content": content,
        })
        result = await self.analysis.analyze(prompt)
        return result.analysis
