import dataclasses
import subprocess
import tempfile

from dev_observer.analysis.repository.provider import GitRepositoryProvider, RepositoryInfo
from dev_observer.common.log import dynamic_logger

_log = dynamic_logger("cloner")


@dataclasses.dataclass
class CloneResult:
    """Result of cloning a repository."""
    path: str
    repo: RepositoryInfo


def clone_repository(
        url: str,
        provider: GitRepositoryProvider,
        max_size_kb: int = 100_000,  # Default max size: 100MB
) -> CloneResult:
    repo = provider.get_repo(url)
    log = _log.bind(repo=repo, url=url)
    if repo.size_kb > max_size_kb:
        raise ValueError(
            f"Repository size ({repo.size_kb} KB) exceeds the maximum allowed size ({max_size_kb} KB)"
        )

    temp_dir = tempfile.mkdtemp(prefix=f"git_repo_{repo.name}")
    log = log.bind(dest=temp_dir)
    log.debug("Cloning...")
    clone_url = provider.get_private_clone_url(repo)
    result = subprocess.run(
        ["git", "clone", "--depth=1", clone_url, temp_dir],
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to clone repository: {result.stderr}")
    log.debug("Cloned.")
    return CloneResult(path=temp_dir, repo=repo)
