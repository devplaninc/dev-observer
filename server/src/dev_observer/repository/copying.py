import subprocess

from dev_observer.repository.parser import parse_github_url
from dev_observer.repository.provider import GitRepositoryProvider, RepositoryInfo


class CopyingGitRepositoryProvider(GitRepositoryProvider):
    def get_repo(self, url: str) -> RepositoryInfo:
        parsed = parse_github_url(url)
        return RepositoryInfo(
            owner=parsed.owner,
            name=parsed.name,
            clone_url=url,
            # TODO: collect actual size.
            size_kb=500,
        )

    def clone(self, repo: RepositoryInfo, dest: str):
        repo_root = _get_git_root()
        result = subprocess.run(
            ["cp", "-r", repo_root, dest],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to copy repository: {result.stderr}")


def _get_git_root() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    return result.stdout.strip()
