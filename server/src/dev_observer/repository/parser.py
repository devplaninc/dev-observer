import dataclasses


@dataclasses.dataclass
class ParsedRepoUrl:
    owner: str
    name: str

    def get_full_name(self) -> str:
        return f"{self.owner}/{self.name}"


def parse_github_url(github_url: str) -> ParsedRepoUrl:
    # Remove trailing slash if present
    github_url = github_url.rstrip('/')
    # Remove .git extension if present
    if github_url.endswith('.git'):
        github_url = github_url[:-4]

    if github_url.startswith('git@github.com:'):
        parts = github_url.split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid GitHub URL: {github_url}")
        owner_repo = parts[1].split('/')
        if len(owner_repo) != 2:
            raise ValueError(f"Invalid GitHub URL: {github_url}")
        owner = owner_repo[0]
        repo_name = owner_repo[1]
    # Handle HTTPS and Git protocol formats
    else:
        parts = github_url.split('/')
        # Check if it's a valid GitHub URL
        if len(parts) < 3 or 'github.com' not in parts:
            raise ValueError(f"Invalid GitHub URL: {github_url}")

        # Find the index of 'github.com' in the parts
        github_index = parts.index('github.com')

        # Owner and repo should be right after 'github.com'
        if len(parts) < github_index + 3:
            raise ValueError(f"Invalid GitHub URL: {github_url}")

        owner = parts[github_index + 1]
        repo_name = parts[github_index + 2]

    return ParsedRepoUrl(owner, repo_name)


