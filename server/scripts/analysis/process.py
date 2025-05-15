import argparse

from dotenv import load_dotenv

load_dotenv()

from dev_observer.analysis.repository.summarizer import process_repository
from dev_observer.common.log import setup_log

setup_log()

from dev_observer.analysis.repository.github_provider import github_provider_from_env

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clones and processes a repo")
    parser.add_argument('--repo', type=str, help='Repository url')
    args = parser.parse_args()

    # Access the arguments
    print(f"Repo url: {args.repo}")
    gh = github_provider_from_env()
    if gh is None:
        raise ValueError("No github provider found")

    result = process_repository(args.repo, gh, cleanup=False)
