import dataclasses
import logging
import tempfile

from dev_observer.api.types.config_pb2 import GlobalConfig
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
        config: GlobalConfig,
) -> CloneResult:
    max_size_kb = 100_000
    if config.repo_analysis.HasField("flatten"):
        max_size_kb = config.repo_analysis.flatten.max_repo_size_mb * 1024
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
