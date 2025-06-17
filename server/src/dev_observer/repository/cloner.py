import dataclasses
import logging
import tempfile

from dev_observer.log import s_
from dev_observer.repository.types import ObservedRepo
from dev_observer.repository.provider import GitRepositoryProvider, RepositoryInfo

_log = logging.getLogger(__name__)


@dataclasses.dataclass
class CloneResult:
    """Result of cloning a repository."""
    path: str
    repo: RepositoryInfo


async def clone_repository(
        repo: ObservedRepo,
        provider: GitRepositoryProvider,
        max_size_kb: int = 100_000,  # Default max size: 100MB
) -> CloneResult:
    info = await provider.get_repo(repo)
    if info.size_kb > max_size_kb:
        raise ValueError(
            f"Repository size ({info.size_kb} KB) exceeds the maximum allowed size ({max_size_kb} KB)"
        )

    temp_dir = tempfile.mkdtemp(prefix=f"git_repo_{info.name}")
    extra = {"repo": repo, "info": info, "dest": temp_dir}
    _log.debug(s_("Cloning...", **extra))
    await provider.clone(repo, info, temp_dir)
    _log.debug(s_("Cloned.", **extra))
    return CloneResult(path=temp_dir, repo=info)
