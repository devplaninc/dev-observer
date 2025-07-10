from abc import abstractmethod
from typing import Protocol, Optional

from dev_observer.api.types.config_pb2 import WebsiteCrawlingConfig


class WebsiteCrawlerProvider(Protocol):
    @abstractmethod
    async def crawl(self, url: str, dest: str, crawling_config: Optional[WebsiteCrawlingConfig] = None):
        """
        Crawl a website and store the data in the specified destination.
        
        Args:
            url: The URL of the website to crawl.
            dest: The destination directory where the crawled data will be stored.
            crawling_config: Optional crawling configuration parameters.
        """
        ...