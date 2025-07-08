import logging
from datetime import datetime
from typing import List, Dict, Any

from github import Auth, Github
from github.PaginatedList import PaginatedList

from dev_observer.log import s_
from dev_observer.repository.github import GithubAuthProvider
from dev_observer.repository.types import ObservedRepo
from dev_observer.storage.provider import StorageProvider

_log = logging.getLogger(__name__)


class GitHubRepositoryProvider:
    _auth_provider: GithubAuthProvider
    _storage: StorageProvider

    def __init__(self, auth_provider: GithubAuthProvider, storage: StorageProvider):
        self._auth_provider = auth_provider
        self._storage = storage

    async def get_commits_since(self, full_name: str, since_date: datetime) -> List[Dict[str, Any]]:
        _log.info(s_("Getting commits since date", repo=full_name, since_date=since_date.isoformat()))
        
        # Get repository from storage to create ObservedRepo
        repo_entity = await self._storage.get_github_repo_by_full_name(full_name)
        if repo_entity is None:
            raise ValueError(f"Repository {full_name} not found in storage")
        
        observed_repo = ObservedRepo(url=repo_entity.url, github_repo=repo_entity)
        auth = await self._auth_provider.get_auth(observed_repo)
        
        commits = []
        try:
            with Github(auth=auth) as gh:
                gh_repo = gh.get_repo(full_name)
                
                # Get commits since the specified date
                repo_commits = gh_repo.get_commits(since=since_date)
                
                # Convert to list with limited fields
                for commit in repo_commits:
                    try:
                        commits.append({
                            "sha": commit.sha,
                            "message": commit.commit.message.split('\n')[0][:100],  # First line, max 100 chars
                            "author": commit.commit.author.name if commit.commit.author else "Unknown",
                            "date": commit.commit.author.date.isoformat() if commit.commit.author else None,
                            "url": commit.html_url
                        })
                    except Exception as e:
                        _log.warning(s_("Failed to process commit", sha=commit.sha, error=str(e)))
                        continue
                        
        except Exception as e:
            _log.error(s_("Failed to get commits", repo=full_name, error=str(e)), exc_info=e)
            raise
        
        _log.info(s_("Retrieved commits", repo=full_name, count=len(commits)))
        return commits

    async def get_merged_prs_since(self, full_name: str, since_date: datetime) -> List[Dict[str, Any]]:
        _log.info(s_("Getting merged PRs since date", repo=full_name, since_date=since_date.isoformat()))
        
        # Get repository from storage to create ObservedRepo
        repo_entity = await self._storage.get_github_repo_by_full_name(full_name)
        if repo_entity is None:
            raise ValueError(f"Repository {full_name} not found in storage")
        
        observed_repo = ObservedRepo(url=repo_entity.url, github_repo=repo_entity)
        auth = await self._auth_provider.get_auth(observed_repo)
        
        merged_prs = []
        try:
            with Github(auth=auth) as gh:
                gh_repo = gh.get_repo(full_name)
                
                # Get closed pull requests and filter for merged ones since the date
                pull_requests = gh_repo.get_pulls(state="closed", sort="updated", direction="desc")
                
                for pr in pull_requests:
                    try:
                        # Check if PR was merged and after the since_date
                        if pr.merged and pr.merged_at and pr.merged_at >= since_date:
                            merged_prs.append({
                                "number": pr.number,
                                "title": pr.title[:100],  # Max 100 chars
                                "user": pr.user.login if pr.user else "Unknown",
                                "merged_at": pr.merged_at.isoformat(),
                                "url": pr.html_url,
                                "body": (pr.body[:200] + "...") if pr.body and len(pr.body) > 200 else pr.body
                            })
                        elif pr.merged_at and pr.merged_at < since_date:
                            # PRs are sorted by updated date, but we can break early if we find old merged PRs
                            # since we're looking for recently merged ones
                            break
                            
                    except Exception as e:
                        _log.warning(s_("Failed to process PR", number=pr.number, error=str(e)))
                        continue
                        
        except Exception as e:
            _log.error(s_("Failed to get merged PRs", repo=full_name, error=str(e)), exc_info=e)
            raise
        
        _log.info(s_("Retrieved merged PRs", repo=full_name, count=len(merged_prs)))
        return merged_prs