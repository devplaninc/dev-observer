import asyncio
import logging
import os

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

        cmd = [
            "python3",
            script_path,
            url,
            "--output-dir",
            dest,
        ]

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

            await asyncio.gather(
                read_stream(process.stdout, stdout_accum, lambda msg: None),
                read_stream(process.stderr, stderr_accum, lambda msg: None)
            )
            code = await process.wait()
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
