import argparse
import logging

import dev_observer.log
from dev_observer.flatten.flatten import flatten_repository
from dev_observer.log import s_
from dev_observer.settings import settings

dev_observer.log.encoder = dev_observer.log.PlainTextEncoder()
logging.basicConfig(level=logging.DEBUG)
_log = logging.getLogger(__name__)

from dev_observer.repository.github_provider import detect_github_provider

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clones and processes a repo")
    parser.add_argument('--repo', type=str, help='Repository url')
    args = parser.parse_args()

    # Access the arguments
    _log.debug(s_("Processing repo", repo=args.repo))
    _log.debug(s_("Loaded settings", gh_auth_type=settings.github.auth_type))
    gh = detect_github_provider()
    if gh is None:
        raise ValueError("No github provider found")

    result = flatten_repository(args.repo, gh, cleanup=False)
