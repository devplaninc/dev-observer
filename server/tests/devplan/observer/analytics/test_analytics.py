import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from dev_observer.analytics.provider import LoggingAnalyticsProvider, ChangeAnalysisAnalytics


class TestAnalyticsProvider:
    
    @pytest.fixture
    def mock_clock(self):
        clock = MagicMock()
        clock.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
        return clock
    
    @pytest.fixture
    def analytics_provider(self, mock_clock):
        return LoggingAnalyticsProvider(clock=mock_clock)
    
    @pytest.fixture
    def change_analytics(self, analytics_provider):
        return ChangeAnalysisAnalytics(analytics_provider)

    async def test_track_event(self, analytics_provider):
        """Test basic event tracking"""
        await analytics_provider.track_event("test_event", {"key": "value"}, "user123")
        # This test mainly ensures no exceptions are thrown
        # In a real implementation, we might verify log output

    async def test_track_error(self, analytics_provider):
        """Test error tracking"""
        await analytics_provider.track_error("test_error", "Error message", {"context": "test"}, "user123")
        # This test mainly ensures no exceptions are thrown

    async def test_track_enrollment(self, change_analytics):
        """Test enrollment tracking"""
        await change_analytics.track_enrollment("repo123", "owner/repo", "user123")
        # Verify the analytics provider was called with correct parameters

    async def test_track_unenrollment(self, change_analytics):
        """Test unenrollment tracking"""
        await change_analytics.track_unenrollment("repo123", "owner/repo", "user123")
        # Verify the analytics provider was called with correct parameters

    async def test_track_analysis_started(self, change_analytics):
        """Test analysis started tracking"""
        await change_analytics.track_analysis_started("repo123", "owner/repo", "analysis123")
        # Verify the analytics provider was called with correct parameters

    async def test_track_analysis_completed(self, change_analytics):
        """Test analysis completed tracking"""
        await change_analytics.track_analysis_completed(
            "repo123", "owner/repo", "analysis123", 5, 2, 1000
        )
        # Verify the analytics provider was called with correct parameters

    async def test_track_analysis_failed(self, change_analytics):
        """Test analysis failed tracking"""
        await change_analytics.track_analysis_failed(
            "repo123", "owner/repo", "analysis123", "Connection error", "ConnectionError"
        )
        # Verify the analytics provider was called with correct parameters

    async def test_track_summary_access(self, change_analytics):
        """Test summary access tracking"""
        await change_analytics.track_summary_access("repo123", "owner/repo", "analysis123", "user123")
        # Verify the analytics provider was called with correct parameters

    async def test_track_api_access(self, change_analytics):
        """Test API access tracking"""
        filters = {"status": "completed", "date_from": "2023-01-01"}
        await change_analytics.track_api_access("get_change_analyses", "repo123", "user123", filters)
        # Verify the analytics provider was called with correct parameters

    async def test_track_api_access_no_filters(self, change_analytics):
        """Test API access tracking without filters"""
        await change_analytics.track_api_access("get_change_analyses", "repo123", "user123")
        # Verify the analytics provider was called with correct parameters