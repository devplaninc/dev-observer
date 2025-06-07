import logging
import os
import subprocess

from dev_observer.log import s_
from dev_observer.website.provider import WebsiteCrawlerProvider

_log = logging.getLogger(__name__)


class ScrapyWebsiteCrawlerProvider(WebsiteCrawlerProvider):
    async def crawl(self, url: str, dest: str):
        os.makedirs(dest, exist_ok=True)
        # Get the directory of the current file
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        # Build the absolute path to the scrapy main.py script relative to this file
        script_path = os.path.join(current_file_dir, 'scrapy', 'main.py')

        # Compose the command
        cmd = [
            "python3",
            script_path,
            url,
            "--output-dir",
            dest
        ]

        # Run the script as subprocess
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            _log.debug(s_("Crawler ran successfully", url=url, dest=dest, out=result.stdout))
        else:
            raise RuntimeError(f"Crawler failed: {result.stderr}")
