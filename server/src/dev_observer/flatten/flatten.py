import dataclasses
import logging
import os
import random
import shutil
import string
import subprocess
from typing import List, Callable, Optional

from dev_observer.log import s_
from dev_observer.repository.cloner import clone_repository
from dev_observer.repository.provider import GitRepositoryProvider, RepositoryInfo
from dev_observer.tokenizer.provider import TokenizerProvider

_log = logging.getLogger(__name__)
_ignore = "**/*.o,**/*.obj,**/*.exe,**/*.dll,**/*.so,**/*.dylib,**/*.a,**/*.class,**/*.jar,**/*.pyc,**/*.pyo,**/*.pyd,**/*.wasm,**/*.bin,**/*.lock,**/*.zip,**/*.tar,**/*.gz,**/*.rar,**/*.7z,**/*.egg,**/*.whl,**/*.deb,**/*.rpm,**/*.png,**/*.jpg,**/*.jpeg,**/*.gif,**/*.svg,**/*.ico,**/*.mp3,**/*.mp4,**/*.mov,**/*.webm,**/*.wav,**/*.ttf,**/*.woff,**/*.woff2,**/*.eot,**/*.otf,**/*.pdf,**/*.ai,**/*.psd,**/*.sketch,**/*.csv,**/*.tsv,**/*.json,**/*.xml,**/*.log,**/*.db,**/*.sqlite,**/*.h5,**/*.parquet,**/*.min.js,**/*.map,**/*.min.css,**/*.bundle.js,**/.DS_Store,**/*.swp,**/*.swo,**/*.iml,**/*.pb.go,**/*_pb2.py*"


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


def combine_repository(repo_path: str) -> CombineResult:
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    folder_path = os.path.join(repo_path, f"devplan_tmp_repomix_{suffix}")
    os.makedirs(folder_path)
    output_file = os.path.join(folder_path, "full.md")
    _log.debug(s_("Executing repomix...", output_file=output_file))
    # Run repomix to combine the repository into a single file
    result = subprocess.run(
        ["repomix",
         "--output", output_file,
         "--ignore", _ignore,
         "--style", "markdown",
         repo_path],
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
        max_tokens_per_file: int = 100_000,
) -> TokenizeResult:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

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
        url: str,
        provider: GitRepositoryProvider,
        tokenizer: TokenizerProvider,
        max_size_kb: int = 100_000,
        max_tokens_per_file: int = 100_000,
) -> FlattenRepoResult:
    clone_result = await clone_repository(url, provider, max_size_kb)
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

    combine_result = combine_repository(repo_path)
    combined_file_path = combine_result.file_path
    out_dir = combine_result.output_dir
    _log.debug(s_("Tokenizing..."))
    tokenize_result = _tokenize_file(combined_file_path, out_dir, tokenizer, max_tokens_per_file)
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
