from abc import abstractmethod
from typing import Protocol


class WebsiteCrawlerProvider(Protocol):
    @abstractmethod
    async def crawl(self, url: str, dest: str):
        """
        Crawl a website and store the data in the specified destination.
        
        Args:
            website: Information about the website to crawl.
            dest: The destination directory where the crawled data will be stored.
        """
        ...