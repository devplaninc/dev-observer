import argparse
import logging
import os
import traceback
import urllib.parse
from typing import Any

from scrapy import Request
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule, CrawlSpider
from scrapy.utils.project import get_project_settings

from dev_observer.website.scrapy.clean_html import clean_html_for_llm

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

class WebsiteCrawlSpider(CrawlSpider):
    """Scrapy spider for crawling websites and saving HTML content."""

    name = 'website_crawler'

    rules = (
        Rule(
            LinkExtractor(
                allow=(),
                deny=(r'\.(js|css|jpg|jpeg|png|gif|svg|pdf|zip|tar|gz|mp3|mp4|mov|webm|wav)$',)
            ),
            callback='parse_item',
            follow=True,
            errback='handle_error'
        ),
    )

    def __init__(
            self,
            url: str,
            output_dir: str,
            *args,
            **kwargs
    ):
        self.start_urls = [url]
        self.output_dir = output_dir

        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc
        domains = [domain]
        if not domain.startswith('www.'):
            domains.append(f"www.{domain}")
        self.allowed_domains = domains

        print(f"Setting up crawler allowed_domains={self.allowed_domains} output_dir={self.output_dir} start_urls={self.start_urls}")

        super().__init__(*args, **kwargs)

    async def start(self):
        print("Start crawling spider")

        for url in self.start_urls:
            request = Request(
                url=url,
                callback=self.parse,
                dont_filter=True,
                meta={'dont_cache': True}
            )
            print(f"Request created url={url}")
            yield request

    def handle_error(self, failure):
        # Try to get more details
        if hasattr(failure.value, 'response'):
            response = failure.value.response
            print(f"Response status: {response.status}")
            print(f"Response headers: {dict(response.headers)}")

    def parse(self, response: Response, **kwargs: Any) -> Any:
        """Override parse method to handle start URLs"""
        print(f"PARSE called for {response.url}")

        # Process the current page
        yield from self.parse_item(response)

        # Let CrawlSpider handle the rules for following links
        yield from self._requests_to_follow(response)

    def parse_item(self, response: Response):
        try:
            print(f"PARSE_ITEM called for {response.url}")
            cleaned_html = clean_html_for_llm(response.text)

            # Create a file path based on the URL
            from urllib.parse import urlparse
            parsed_url = urlparse(response.url)

            # Create directory structure based on URL path
            path_parts = parsed_url.path.strip('/').split('/')
            if not path_parts or path_parts[0] == '':
                # Root page
                file_name = 'index.html'
                dir_path = self.output_dir
            else:
                # Nested page
                file_name = path_parts[-1]
                if not file_name:
                    file_name = 'index.html'
                if '.' not in file_name:
                    file_name = f"{file_name}.html"
                dir_path = os.path.join(self.output_dir, *path_parts[:-1])

            os.makedirs(dir_path, exist_ok=True)
            file_path = os.path.join(dir_path, file_name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_html)

            print(f"Saved HTML content path_parts={path_parts} url={response.url}, file={file_path}")

            yield {
                'url': response.url,
                'file': file_path
            }
        except Exception as e:
            print(f"Error parsing response url={response.url} error={e} trace={traceback.format_exc()}")
            raise e


def main():
    """Run the test script."""
    parser = argparse.ArgumentParser(description="Test the website crawler.")
    parser.add_argument("url", help="The URL of the website to crawl.")
    parser.add_argument("--output-dir",
                        help="The directory to store the crawled data. If not provided, a temporary directory will be used.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging.")
    args = parser.parse_args()

    if args.verbose == "true":
        logging.getLogger().setLevel(logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)
        logging.basicConfig(level=logging.INFO)

    settings = get_project_settings()
    settings.update({
        'TELNETCONSOLE_ENABLED': False,
        'USER_AGENT': 'Mozilla/5.0 (compatible; DevObserverBot/1.0)',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 3,
        # 'DOWNLOAD_DELAY': 0.5,  # Be polite with requests
        'DEPTH_LIMIT': 2,
        'CLOSESPIDER_PAGECOUNT': 20,
        'LOG_LEVEL': 'DEBUG' if args.verbose else 'INFO',
        'REDIRECT_ENABLED': True,
        'REDIRECT_MAX_TIMES': 20,
    })
    process = CrawlerProcess(settings=settings)
    print(f"Starting crawler args={args}")
    process.crawl(WebsiteCrawlSpider, url=args.url, output_dir=args.output_dir)
    process.start()


if __name__ == "__main__":
    main()
