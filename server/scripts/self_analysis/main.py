import asyncio
import logging
import os
import subprocess

from dotenv import load_dotenv

import dev_observer.log
from dev_observer.env_detection import detect_processor
from dev_observer.log import s_
from dev_observer.settings import Settings

dev_observer.log.encoder = dev_observer.log.PlainTextEncoder()
logging.basicConfig(level=logging.DEBUG)
_log = logging.getLogger(__name__)

_repo = "git@github.com:devplaninc/dev-observer.git"


def get_git_root() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    return result.stdout.strip()


async def main():
    repo_root = get_git_root()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(repo_root, "server", ".env"))
    load_dotenv(os.path.join(repo_root, "server", ".env.local"))

    os.environ["DEV_OBSERVER__PROMPTS__LOCAL__DIR"] = os.path.join(current_dir, "prompts")
    Settings.model_config["toml_file"] = os.path.join(current_dir, "config.toml")
    processor = detect_processor(Settings())
    analysis = await processor.process("self", _repo)
    out_md = os.path.join(repo_root, "REPO_ANALYSIS.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(str(analysis))
    _log.info(s_("Analysis saved", out_file=out_md))


if __name__ == "__main__":
    asyncio.run(main())
