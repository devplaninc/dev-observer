import asyncio
import logging
import os
from typing import Optional

from dev_observer.api.types.config_pb2 import WebsiteCrawlingConfig
from dev_observer.log import s_
from dev_observer.website.provider import WebsiteCrawlerProvider

_log = logging.getLogger(__name__)


class ScrapyWebsiteCrawlerProvider(WebsiteCrawlerProvider):
    async def crawl(self, url: str, dest: str, crawling_config: Optional[WebsiteCrawlingConfig] = None):
        os.makedirs(dest, exist_ok=True)
        # Get the directory of the current file
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        # Build the absolute path to the scrapy main.py script relative to this file
        script_path = os.path.join(current_file_dir, 'scrapy', 'main.py')

        cmd = [
            "python3",
            script_path,
            url,
            "--output-dir",
            dest,
        ]
        
        # Add crawling config parameters if provided
        if crawling_config:
            if crawling_config.scrapy_response_timeout_seconds:
                crawler_timeout = crawling_config.scrapy_response_timeout_seconds
                if crawler_timeout > 1:
                    crawler_timeout = crawler_timeout - 1
                cmd.extend(["--response-timeout", str(crawler_timeout)])
            if crawling_config.crawl_depth:
                cmd.extend(["--depth-limit", str(crawling_config.crawl_depth)])
            if crawling_config.timeout_without_data_seconds:
                cmd.extend(["--timeout-no-item", str(crawling_config.timeout_without_data_seconds)])

        # Determine overall scan timeout
        scan_timeout = None
        if crawling_config and crawling_config.website_scan_timeout_seconds:
            scan_timeout = crawling_config.website_scan_timeout_seconds

        # Run the script asynchronously
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        extra = {"op": "crawl_site", "url": url, "dest": dest}

        stdout_accum = []
        stderr_accum = []
        try:
            async def read_stream(stream, accum, log_fn):
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    decoded = line.decode().rstrip()
                    accum.append(decoded)
                    log_fn(decoded)

            async def run_crawler():
                await asyncio.gather(
                    read_stream(process.stdout, stdout_accum, lambda msg: None),
                    read_stream(process.stderr, stderr_accum, lambda msg: None)
                )
                return await process.wait()

            if scan_timeout:
                code = await asyncio.wait_for(run_crawler(), timeout=scan_timeout)
            else:
                code = await run_crawler()
        except asyncio.TimeoutError as e:
            _log.error(s_("Crawler timed out", error=e, **extra,
                          stdout="\n".join(stdout_accum),
                          stderr="\n".join(stderr_accum)))
            process.kill()
            raise RuntimeError(f"Website crawl timed out after {scan_timeout} seconds")
        except asyncio.CancelledError as e:
            _log.error(s_("Crawler cancelled", error=e, **extra,
                          stdout="\n".join(stdout_accum),
                          stderr="\n".join(stderr_accum)))
            process.kill()
            raise
        except Exception as e:
            _log.error(s_("Crawler failed", error=e, **extra,
                          stdout="\n".join(stdout_accum),
                          stderr="\n".join(stderr_accum)))
            raise

        if code == 0:
            _log.debug(s_("Crawler ran successfully", **extra))
        else:
            full_stderr = "\n".join(stderr_accum)
            raise RuntimeError(f"Crawler failed: code={code}, stderr={full_stderr}")
