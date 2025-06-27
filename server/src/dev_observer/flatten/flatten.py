import dataclasses
import logging
import os
import random
import shutil
import string
import subprocess
from typing import List, Callable, Optional

from dev_observer.api.types.config_pb2 import GlobalConfig, RepoAnalysisConfig
from dev_observer.log import s_
from dev_observer.repository.cloner import clone_repository
from dev_observer.repository.provider import GitRepositoryProvider, RepositoryInfo
from dev_observer.repository.types import ObservedRepo
from dev_observer.tokenizer.provider import TokenizerProvider

_log = logging.getLogger(__name__)


@dataclasses.dataclass
class CombineResult:
    """Result of combining a repository into a single file."""
    file_path: str
    size_bytes: int
    output_dir: str


@dataclasses.dataclass
class FlattenResult:
    full_file_path: str
    """Result of breaking down a file into smaller files based on token count."""
    file_paths: List[str]
    total_tokens: int
    clean_up: Callable[[], bool]


def combine_repository(repo_path: str, info: RepositoryInfo, config: GlobalConfig) -> CombineResult:
    flatten_config = config.repo_analysis.flatten if config.repo_analysis.HasField("flatten") \
        else RepoAnalysisConfig.Flatten()
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    folder_path = os.path.join(repo_path, f"devplan_tmp_repomix_{suffix}")
    os.makedirs(folder_path)
    output_file = os.path.join(folder_path, "full.md")

    large_threshold_kb = (flatten_config.large_repo_threshold_mb or 500) * 1024
    is_large = info.size_kb > large_threshold_kb
    _log.info(s_("Starting repo flatten", is_large=is_large))

    compress = flatten_config.compress or (is_large and flatten_config.compress_large)
    ignore = flatten_config.ignore_pattern
    if is_large and len(flatten_config.large_repo_ignore_pattern) > 0:
        ignore = ",".join([ignore, flatten_config.large_repo_ignore_pattern])

    # Run repomix to combine the repository into a single file
    cmd = ["repomix",
           "--output", output_file,
           "--ignore", ignore,
           "--style", flatten_config.out_style if len(flatten_config.out_style) > 0 else "markdown"]
    if compress:
        cmd.append("--compress")
    cmd.append(repo_path)

    _log.debug(s_("Executing repomix...", output_file=output_file, cmd=cmd))
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        _log.error(s_("Failed to repomix repository.", out=result.stderr, code=result.returncode))
        raise RuntimeError(f"Failed to combine repository: {result.stderr}")

    _log.debug(s_("Done.", out=result.stdout))

    # Get the size of the combined file
    size_bytes = os.path.getsize(output_file)

    return CombineResult(file_path=output_file, size_bytes=size_bytes, output_dir=folder_path)


@dataclasses.dataclass
class TokenizeResult:
    """Result of breaking down a file into smaller files based on token count."""
    file_paths: List[str]
    total_tokens: int


def _tokenize_file(
        file_path: str,
        out_dir: str,
        tokenizer: TokenizerProvider,
        config: GlobalConfig,
) -> TokenizeResult:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    max_tokens_per_file = 100_000
    if config.repo_analysis.HasField("flatten"):
        max_tokens_per_file = config.repo_analysis.flatten.max_tokens_per_chunk
    if max_tokens_per_file <= 0:
        raise ValueError("max_tokens_per_file must be greater than 0")

    # Read the input file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Tokenize the content
    tokens = tokenizer.encode(content)
    total_tokens = len(tokens)
    if total_tokens <= max_tokens_per_file:
        return TokenizeResult(file_paths=[], total_tokens=total_tokens)

    # Create output files
    output_files = []
    for i in range(0, total_tokens, max_tokens_per_file):
        chunk_tokens = tokens[i:i + max_tokens_per_file]
        chunk_text = tokenizer.decode(chunk_tokens)
        out_file = os.path.join(out_dir, f"chunk_{i}.md")
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(chunk_text)

        output_files.append(out_file)

    return TokenizeResult(file_paths=output_files, total_tokens=total_tokens)


@dataclasses.dataclass
class FlattenRepoResult:
    flatten_result: FlattenResult
    repo: RepositoryInfo


async def flatten_repository(
        repo: ObservedRepo,
        provider: GitRepositoryProvider,
        tokenizer: TokenizerProvider,
        config: GlobalConfig,
) -> FlattenRepoResult:
    clone_result = await clone_repository(repo, provider, config)
    repo_path = clone_result.path
    combined_file_path: Optional[str] = None

    def clean_up():
        cleaned = False
        if os.path.exists(repo_path):
            shutil.rmtree(repo_path)
            cleaned = True
        if clean_up is not None and os.path.exists(combined_file_path):
            os.remove(combined_file_path)
            cleaned = True
        return cleaned

    combine_result = combine_repository(repo_path, clone_result.repo, config)
    combined_file_path = combine_result.file_path
    out_dir = combine_result.output_dir
    _log.debug(s_("Tokenizing..."))
    tokenize_result = _tokenize_file(combined_file_path, out_dir, tokenizer, config)
    _log.debug(s_("File tokenized"))
    flatten_result = FlattenResult(
        full_file_path=combined_file_path,
        file_paths=tokenize_result.file_paths,
        total_tokens=tokenize_result.total_tokens,
        clean_up=clean_up,
    )
    return FlattenRepoResult(
        flatten_result=flatten_result,
        repo=clone_result.repo,
    )
