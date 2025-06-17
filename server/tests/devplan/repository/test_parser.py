import unittest

from dev_observer.repository.parser import parse_github_url, ParsedRepoUrl


class TestParseGithubUrl(unittest.TestCase):
    def test_ssh_url(self):
        # Test SSH URL format
        url = "git@github.com:owner/repo"
        result = parse_github_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")
        self.assertEqual(result.get_full_name(), "owner/repo")

    def test_https_url(self):
        # Test HTTPS URL format
        url = "https://github.com/owner/repo"
        result = parse_github_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")
        self.assertEqual(result.get_full_name(), "owner/repo")

    def test_http_url(self):
        # Test HTTP URL format
        url = "http://github.com/owner/repo"
        result = parse_github_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_url_with_trailing_slash(self):
        # Test URL with trailing slash
        url = "https://github.com/owner/repo/"
        result = parse_github_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_cli_url(self):
        # Test URL with trailing slash
        url = "https://github.com/devplaninc/devplan-cli"
        result = parse_github_url(url)
        self.assertEqual(result.owner, "devplaninc")
        self.assertEqual(result.name, "devplan-cli")
        self.assertEqual(result.get_full_name(), "devplaninc/devplan-cli")

    def test_url_with_git_extension(self):
        # Test URL with .git extension
        url = "https://github.com/owner/repo.git"
        result = parse_github_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")

    def test_ssh_url_with_git_extension(self):
        # Test SSH URL with .git extension
        url = "git@github.com:owner/repo.git"
        result = parse_github_url(url)
        self.assertEqual(result.owner, "owner")
        self.assertEqual(result.name, "repo")


    def test_invalid_ssh_url(self):
        # Test invalid SSH URL format
        with self.assertRaises(ValueError):
            parse_github_url("git@github.com:invalid")

    def test_invalid_https_url(self):
        # Test invalid HTTPS URL format
        with self.assertRaises(ValueError):
            parse_github_url("https://github.com/invalid")

    def test_non_github_url(self):
        # Test non-GitHub URL
        with self.assertRaises(ValueError):
            parse_github_url("https://gitlab.com/owner/repo")

    def test_empty_url(self):
        # Test empty URL
        with self.assertRaises(ValueError):
            parse_github_url("")

    def test_parsed_repo_url_class(self):
        # Test ParsedRepoUrl class
        repo = ParsedRepoUrl(owner="owner", name="repo")
        self.assertEqual(repo.owner, "owner")
        self.assertEqual(repo.name, "repo")
        self.assertEqual(repo.get_full_name(), "owner/repo")
