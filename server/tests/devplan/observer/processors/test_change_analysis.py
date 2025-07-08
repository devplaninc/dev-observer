import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from dev_observer.api.types.repo_pb2 import RepoChangeAnalysis, GitHubRepository
from dev_observer.analytics.provider import ChangeAnalysisAnalytics, LoggingAnalyticsProvider
from dev_observer.processors.change_analysis import ChangeAnalysisProcessor


class TestChangeAnalysisProcessor:
    
    @pytest.fixture
    def mock_storage(self):
        storage = MagicMock()
        storage.get_enrolled_repos_for_change_analysis = AsyncMock(return_value=[])
        storage.get_github_repo = AsyncMock()
        storage.create_repo_change_analysis = AsyncMock()
        storage.get_repo_change_analyses_by_repo = AsyncMock(return_value=[])
        storage.update_repo_change_analysis_status = AsyncMock()
        storage.set_repo_change_analysis_observation = AsyncMock()
        return storage
    
    @pytest.fixture
    def mock_github_provider(self):
        provider = MagicMock()
        provider.get_commits_since = AsyncMock(return_value=[])
        provider.get_merged_prs_since = AsyncMock(return_value=[])
        return provider
    
    @pytest.fixture
    def mock_analysis_provider(self):
        provider = MagicMock()
        provider.analyze = AsyncMock()
        return provider
    
    @pytest.fixture
    def mock_observations_provider(self):
        provider = MagicMock()
        provider.store_observation = AsyncMock()
        return provider
    
    @pytest.fixture
    def mock_analytics(self):
        analytics_provider = LoggingAnalyticsProvider()
        return ChangeAnalysisAnalytics(analytics_provider)
    
    @pytest.fixture
    def mock_clock(self):
        clock = MagicMock()
        clock.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
        return clock
    
    @pytest.fixture
    def processor(self, mock_storage, mock_github_provider, mock_analysis_provider, 
                  mock_observations_provider, mock_analytics, mock_clock):
        return ChangeAnalysisProcessor(
            storage=mock_storage,
            github_provider=mock_github_provider,
            analysis_provider=mock_analysis_provider,
            observations_provider=mock_observations_provider,
            analytics=mock_analytics,
            clock=mock_clock
        )
    
    @pytest.fixture
    def sample_repo(self):
        repo = GitHubRepository()
        repo.id = str(uuid.uuid4())
        repo.name = "test-repo"
        repo.full_name = "owner/test-repo"
        repo.url = "https://github.com/owner/test-repo"
        return repo

    async def test_run_daily_analysis_no_enrolled_repos(self, processor, mock_storage):
        """Test daily analysis with no enrolled repositories"""
        mock_storage.get_enrolled_repos_for_change_analysis.return_value = []
        
        await processor.run_daily_analysis()
        
        mock_storage.get_enrolled_repos_for_change_analysis.assert_called_once()

    async def test_run_daily_analysis_with_repos(self, processor, mock_storage, sample_repo):
        """Test daily analysis with enrolled repositories"""
        mock_storage.get_enrolled_repos_for_change_analysis.return_value = [sample_repo]
        
        # Mock the _analyze_repository_changes method to avoid full execution
        processor._analyze_repository_changes = AsyncMock()
        
        await processor.run_daily_analysis()
        
        mock_storage.get_enrolled_repos_for_change_analysis.assert_called_once()
        processor._analyze_repository_changes.assert_called_once_with(sample_repo.id)

    async def test_get_todays_analysis_exists(self, processor, mock_storage):
        """Test getting today's analysis when it exists"""
        repo_id = str(uuid.uuid4())
        
        # Create analysis for today
        analysis = RepoChangeAnalysis()
        analysis.id = str(uuid.uuid4())
        analysis.analyzed_at.FromDatetime(datetime(2023, 1, 1, 10, 0, 0))
        
        mock_storage.get_repo_change_analyses_by_repo.return_value = [analysis]
        
        result = await processor._get_todays_analysis(repo_id)
        
        assert result is not None
        assert result.id == analysis.id

    async def test_get_todays_analysis_not_exists(self, processor, mock_storage):
        """Test getting today's analysis when it doesn't exist"""
        repo_id = str(uuid.uuid4())
        
        # Create analysis for yesterday
        analysis = RepoChangeAnalysis()
        analysis.id = str(uuid.uuid4())
        analysis.analyzed_at.FromDatetime(datetime(2022, 12, 31, 10, 0, 0))
        
        mock_storage.get_repo_change_analyses_by_repo.return_value = [analysis]
        
        result = await processor._get_todays_analysis(repo_id)
        
        assert result is None

    async def test_get_recent_changes(self, processor, mock_storage, mock_github_provider, sample_repo):
        """Test getting recent changes from GitHub"""
        repo_id = sample_repo.id
        
        # Mock storage and GitHub provider
        mock_storage.get_github_repo.return_value = sample_repo
        mock_storage.get_repo_change_analyses_by_repo.return_value = []
        
        mock_commits = [{"sha": "abc123", "message": "Test commit"}]
        mock_prs = [{"number": 1, "title": "Test PR"}]
        
        mock_github_provider.get_commits_since.return_value = mock_commits
        mock_github_provider.get_merged_prs_since.return_value = mock_prs
        
        result = await processor._get_recent_changes(repo_id)
        
        assert result["commits"] == mock_commits
        assert result["merged_prs"] == mock_prs
        assert result["repo_name"] == sample_repo.full_name

    def test_format_commits(self, processor):
        """Test commit formatting"""
        commits = [
            {"message": "Add new feature", "author": "John Doe"},
            {"message": "Fix bug", "author": "Jane Smith"}
        ]
        
        result = processor._format_commits(commits)
        
        assert "Add new feature (John Doe)" in result
        assert "Fix bug (Jane Smith)" in result

    def test_format_commits_empty(self, processor):
        """Test formatting empty commits list"""
        result = processor._format_commits([])
        
        assert result == "No commits found"

    def test_format_prs(self, processor):
        """Test PR formatting"""
        prs = [
            {"number": 1, "title": "Add feature", "user": "john"},
            {"number": 2, "title": "Fix issue", "user": "jane"}
        ]
        
        result = processor._format_prs(prs)
        
        assert "#1: Add feature (john)" in result
        assert "#2: Fix issue (jane)" in result

    def test_format_prs_empty(self, processor):
        """Test formatting empty PRs list"""
        result = processor._format_prs([])
        
        assert result == "No merged pull requests found"

    def test_generate_fallback_summary_no_changes(self, processor, sample_repo):
        """Test fallback summary with no changes"""
        changes = {"commits": [], "merged_prs": [], "since_date": "2023-01-01"}
        
        result = processor._generate_fallback_summary(sample_repo, changes)
        
        assert "No significant changes detected" in result
        assert sample_repo.full_name in result

    def test_generate_fallback_summary_with_changes(self, processor, sample_repo):
        """Test fallback summary with changes"""
        changes = {
            "commits": [{"message": "Test commit", "author": "John"}],
            "merged_prs": [{"number": 1, "title": "Test PR"}],
            "since_date": "2023-01-01"
        }
        
        result = processor._generate_fallback_summary(sample_repo, changes)
        
        assert "1 commits" in result
        assert "1 merged pull requests" in result
        assert sample_repo.full_name in result
        assert "Test commit" in result
        assert "#1" in result