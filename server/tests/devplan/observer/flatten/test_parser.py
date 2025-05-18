from dev_observer.repository.parser import parse_github_url
import pytest


class TestParseGithubUrl:
    @pytest.mark.parametrize("url,expected_owner,expected_repo", [
        ("https://github.com/user/repo", "user", "repo"),
        ("https://github.com/user/repo.git", "user", "repo"),
        ("https://github.com/user/repo/", "user", "repo"),
        ("git@github.com:user/repo", "user", "repo"),
        ("git@github.com:user/repo.git", "user", "repo"),
        ("git://github.com/user/repo", "user", "repo"),
        ("git://github.com/user/repo.git", "user", "repo"),
    ])
    def test_valid_github_urls(self, url, expected_owner, expected_repo):
        info = parse_github_url(url)
        assert info.owner == expected_owner
        assert info.name == expected_repo

    @pytest.mark.parametrize("invalid_url", [
        "https://not-github.com/user/repo",
        "https://github.com/user",
        "git@github.com:user",
        "git@github.com/user/repo",
        "not-a-url"
    ])
    def test_invalid_github_urls(self, invalid_url):
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            parse_github_url(invalid_url)
