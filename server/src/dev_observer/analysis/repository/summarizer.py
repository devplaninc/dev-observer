import dataclasses
import os
import random
import shutil
import string
import subprocess
from typing import List

import tiktoken

from dev_observer.analysis.repository.cloner import clone_repository
from dev_observer.analysis.repository.provider import GitRepositoryProvider
from dev_observer.common.log import dynamic_logger

_log = dynamic_logger("summarizer")

_ignore = "**/*.o,**/*.obj,**/*.exe,**/*.dll,**/*.so,**/*.dylib,**/*.a,**/*.class,**/*.jar,**/*.pyc,**/*.pyo,**/*.pyd,**/*.wasm,**/*.bin,**/*.lock,**/*.zip,**/*.tar,**/*.gz,**/*.rar,**/*.7z,**/*.egg,**/*.whl,**/*.deb,**/*.rpm,**/*.png,**/*.jpg,**/*.jpeg,**/*.gif,**/*.svg,**/*.ico,**/*.mp3,**/*.mp4,**/*.mov,**/*.webm,**/*.wav,**/*.ttf,**/*.woff,**/*.woff2,**/*.eot,**/*.otf,**/*.pdf,**/*.ai,**/*.psd,**/*.sketch,**/*.csv,**/*.tsv,**/*.json,**/*.xml,**/*.log,**/*.db,**/*.sqlite,**/*.h5,**/*.parquet,**/*.min.js,**/*.map,**/*.min.css,**/*.bundle.js,**/.DS_Store,**/*.swp,**/*.swo,**/*.iml,**/*.pb.go,**/*_pb2.py*"


@dataclasses.dataclass
class CombineResult:
    """Result of combining a repository into a single file."""
    file_path: str
    size_bytes: int
    output_dir: str


@dataclasses.dataclass
class TokenizedFileResult:
    """Result of breaking down a file into smaller files based on token count."""
    file_paths: List[str]
    total_tokens: int


def combine_repository(repo_path: str) -> CombineResult:
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    folder_path = os.path.join(repo_path, f"devplan_tmp_repomix_{suffix}")
    os.makedirs(folder_path)
    output_file = os.path.join(folder_path, "full.md")
    log = _log.bind(output_file=output_file)

    log.debug("Executing repomix...")
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
        log.error("Failed to repomix repository.", out=result.stderr, code=result.returncode)
        raise RuntimeError(f"Failed to combine repository: {result.stderr}")

    log.debug("Done.", out=result.stdout)

    # Get the size of the combined file
    size_bytes = os.path.getsize(output_file)

    return CombineResult(file_path=output_file, size_bytes=size_bytes, output_dir=folder_path)


def tokenize_file(
        file_path: str,
        out_dir: str,
        max_tokens_per_file: int = 100_000,
) -> TokenizedFileResult:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if max_tokens_per_file <= 0:
        raise ValueError("max_tokens_per_file must be greater than 0")

    # Read the input file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Initialize the tokenizer (using cl100k_base, which is used by GPT-4)
    enc = tiktoken.get_encoding("cl100k_base")

    # Tokenize the content
    tokens = enc.encode(content)
    total_tokens = len(tokens)

    # Create output files
    output_files = []
    for i in range(0, total_tokens, max_tokens_per_file):
        # Get a chunk of tokens
        chunk_tokens = tokens[i:i + max_tokens_per_file]

        # Decode the tokens back to text
        chunk_text = enc.decode(chunk_tokens)

        # Create a temporary file for this chunk
        out_file = os.path.join(out_dir, f"chunk_{i}.md")
        # Write the chunk to the file
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(chunk_text)

        output_files.append(out_file)

    return TokenizedFileResult(file_paths=output_files, total_tokens=total_tokens)


def process_repository(
        url: str,
        provider: GitRepositoryProvider,
        max_size_kb: int = 100_000,
        max_tokens_per_file: int = 100_000,
        cleanup: bool = True,
) -> TokenizedFileResult:
    clone_result = clone_repository(url, provider, max_size_kb)
    repo_path = clone_result.path

    try:
        combine_result = combine_repository(repo_path)
        combined_file_path = combine_result.file_path
        out_dir = combine_result.output_dir
        try:
            tokenize_result = tokenize_file(combined_file_path, out_dir, max_tokens_per_file)
            return tokenize_result
        finally:
            # Clean up the combined file if requested
            if cleanup and os.path.exists(combined_file_path):
                os.remove(combined_file_path)
    finally:
        # Clean up the cloned repository if requested
        if cleanup and os.path.exists(repo_path):
            shutil.rmtree(repo_path)
