import asyncio
import dataclasses
import logging
import os
import re
import tempfile
import urllib.parse
from typing import Optional

from dev_observer.api.types.config_pb2 import WebsiteCrawlingConfig
from dev_observer.log import s_
from dev_observer.website.provider import WebsiteCrawlerProvider

_log = logging.getLogger(__name__)

def normalize_domain(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc
    # Remove www. prefix if present
    if domain.startswith('www.'):
        domain = domain[4:]
    # Replace non-alphanumeric characters with underscores
    domain = re.sub(r'[^a-zA-Z0-9]', '_', domain)
    return domain


def normalize_name(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    # Remove trailing slash
    if path.endswith('/'):
        path = path[:-1]
    # Use the last part of the path as the name, or 'root' if empty
    name = os.path.basename(path) if path else 'root'
    # Replace non-alphanumeric characters with underscores
    name = re.sub(r'[^a-zA-Z0-9]', '_', name)
    # If name is empty, use 'root'
    if not name:
        name = 'root'
    return name


@dataclasses.dataclass
class CrawlResult:
    """Result of crawling a website."""
    path: str
    url: str


async def crawl_website(
        url: str,
        provider: WebsiteCrawlerProvider,
        crawling_config: Optional[WebsiteCrawlingConfig] = None,
) -> CrawlResult:
    name = normalize_name(url)
    domain = normalize_domain(url)
    temp_dir = tempfile.mkdtemp(prefix=f"website_{domain}_{name}_")
    
    timeout = 30
    if crawling_config and crawling_config.website_scan_timeout_seconds:
        timeout = crawling_config.website_scan_timeout_seconds
    
    extra = {"url": url, "dest": temp_dir, "timeout": timeout}
    _log.debug(s_("Crawling website...", **extra))
    try:
        # The provider will handle its own timeout, but we add this as a safety net
        await asyncio.wait_for(provider.crawl(url, temp_dir, crawling_config), timeout=timeout)
    except asyncio.TimeoutError:
        _log.error(s_("Website crawling timed out", **extra))
        raise
    except Exception as e:
        _log.error(s_("Website crawling failed", error=e, **extra))
        raise

    _log.debug(s_("Website crawled.", **extra))
    return CrawlResult(path=temp_dir, url=url)
