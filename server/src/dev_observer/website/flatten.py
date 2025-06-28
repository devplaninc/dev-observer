import dataclasses
import logging
import os
import random
import shutil
import string
from typing import Optional, List, Dict

from dev_observer.flatten.flatten import FlattenResult
from dev_observer.log import s_
from dev_observer.tokenizer.provider import TokenizerProvider
from dev_observer.website.cloner import crawl_website
from dev_observer.website.provider import WebsiteCrawlerProvider

_log = logging.getLogger(__name__)


def _get_files_by_level(website_path: str) -> Dict[int, List[str]]:
    """
    Get all HTML files in the website path, organized by directory level.
    Level 0 is the top level (root directory).
    """
    files_by_level = {}
    for root, _, files in os.walk(website_path):
        # Calculate the level based on the directory depth
        rel_path = os.path.relpath(root, website_path)
        level = 0 if rel_path == '.' else len(rel_path.split(os.sep))

        # Add HTML files to the appropriate level
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                if level not in files_by_level:
                    files_by_level[level] = []
                files_by_level[level].append(file_path)

    return files_by_level

@dataclasses.dataclass
class CombineWebsiteResult:
    output_files: List[str]
    folder_path: str
    total_tokens: int

def combine_website(website_path: str, tokenizer: TokenizerProvider, max_tokens_per_file: int) -> CombineWebsiteResult:
    """
    Combine website files into one or more files, respecting max tokens per file.
    Process files in level order (top level first, then next level, etc.).
    Each entry is prepended with the file name.
    """
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    folder_path = os.path.join(website_path, f"devplan_tmp_website_{suffix}")
    os.makedirs(folder_path)

    # Get files organized by level
    files_by_level = _get_files_by_level(website_path)

    # Sort levels to process top level first
    sorted_levels = sorted(files_by_level.keys())

    all_files = []
    for level in sorted_levels:
        all_files.extend(files_by_level[level])

    # If no files found, create an empty combined file
    if not all_files:
        return CombineWebsiteResult(output_files=[], folder_path=folder_path, total_tokens=0)

    # First pass: compute tokens for all files and prepare their content
    file_contents = []
    total_tokens = 0

    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Get relative path from website_path for the file name header
            rel_path = os.path.relpath(file_path, website_path)
            file_header = f"# File: {rel_path}\n\n"

            # Calculate tokens for this file with header
            file_content = file_header + content
            file_tokens = len(tokenizer.encode(file_content))

            file_contents.append((file_content, file_tokens))
            total_tokens += file_tokens

        except Exception as e:
            _log.error(s_("Error processing file", file=file_path, error=str(e)))

    # Second pass: create output files with appropriate names based on total token count
    use_combined_file = total_tokens <= max_tokens_per_file
    current_chunk = 0
    current_file = None
    current_tokens = 0
    output_files = []

    for file_content, file_tokens in file_contents:
        # If adding this file would exceed max tokens, or if no current file exists,
        # create a new output file
        if current_file is None or current_tokens + file_tokens > max_tokens_per_file:
            # Close current file if it exists
            if current_file is not None:
                current_file.close()

            # Create new file
            if use_combined_file and len(output_files) == 0:
                # If all content fits in one file
                output_path = os.path.join(folder_path, "combined_page.txt")
            else:
                output_path = os.path.join(folder_path, f"chunk_{current_chunk}_page.txt")
                current_chunk += 1

            output_files.append(output_path)
            current_file = open(output_path, 'w', encoding='utf-8')
            current_tokens = 0

        # Write content to current file
        current_file.write(file_content)
        current_file.write("\n\n")
        current_tokens += file_tokens

    # Close the last file if it exists
    if current_file is not None:
        current_file.close()
    return CombineWebsiteResult(
        output_files=output_files if output_files else [],
        folder_path=folder_path,
        total_tokens=total_tokens,
    )


@dataclasses.dataclass
class FlattenWebsiteResult:
    """Result of flattening a website."""
    flatten_result: FlattenResult
    url: str


async def flatten_website(
        url: str,
        provider: WebsiteCrawlerProvider,
        tokenizer: TokenizerProvider,
        max_tokens_per_file: int = 100_000,
) -> FlattenWebsiteResult:
    crawl_result = await crawl_website(url, provider)
    website_path = crawl_result.path
    output_dir: Optional[str] = None

    def clean_up():
        cleaned = False
        if os.path.exists(website_path):
            shutil.rmtree(website_path)
            cleaned = True
        if output_dir is not None and os.path.exists(output_dir):
            shutil.rmtree(output_dir)
            cleaned = True
        return cleaned

    _log.debug(s_("Combining website files..."))
    comb_res = combine_website(website_path, tokenizer, max_tokens_per_file)
    out_files = comb_res.output_files
    output_dir = comb_res.folder_path
    total_tokens=comb_res.total_tokens

    _log.debug(s_("Website flattened", num_files=len(out_files), total_tokens=total_tokens))
    full_file_path=out_files[0] if len(out_files) == 1  else ""

    flatten_result = FlattenResult(
        full_file_path=full_file_path,
        file_paths=[] if len(out_files) == 1 else out_files,
        total_tokens=total_tokens,
        clean_up=clean_up,
    )

    return FlattenWebsiteResult(
        flatten_result=flatten_result,
        url=crawl_result.url,
    )
