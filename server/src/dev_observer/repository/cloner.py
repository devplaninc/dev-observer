import dataclasses
import logging
import tempfile

from dev_observer.log import s_
from dev_observer.repository.provider import GitRepositoryProvider, RepositoryInfo

_log = logging.getLogger(__name__)


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
    if repo.size_kb > max_size_kb:
        raise ValueError(
            f"Repository size ({repo.size_kb} KB) exceeds the maximum allowed size ({max_size_kb} KB)"
        )

    temp_dir = tempfile.mkdtemp(prefix=f"git_repo_{repo.name}")
    extra = {"repo": repo, "url": url, "dest": temp_dir}
    _log.debug(s_("Cloning...", **extra))
    provider.clone(repo, temp_dir)
    _log.debug(s_("Cloned.", **extra))
    return CloneResult(path=temp_dir, repo=repo)
