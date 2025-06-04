#!/usr/bin/env bash

set -ex
set -o pipefail

root=$(git rev-parse --show-toplevel)

export DEV_OBSERVER__PROMPTS__LOCAL__DIR="$root"/scripts/server/dev/prompts
export DEV_OBSERVER__OBSERVATIONS__LOCAL__DIR="$root"/scripts/server/dev/_local_data_
export DEV_OBSERVER__STORAGE__POSTGRESQL__DB_URL="postgresql+asyncpg://postgres:test_password@localhost:54322/dev_observer"
export DEV_OBSERVER_CONFIG_FILE="$root"/scripts/server/dev/config.toml

export DEV_OBSERVER__STORAGE__PROVIDER="local"
export DEV_OBSERVER__STORAGE__LOCAL__DIR="$root"/scripts/server/dev/_local_data_/__storage

# TODO: these things below only needed for offline mode
export DEV_OBSERVER__GIT__PROVIDER="copying"
export DEV_OBSERVER__ANALYSIS__PROVIDER="stub"
export DEV_OBSERVER__TOKENIZER__PROVIDER="stub"
export DEV_OBSERVER__TOKENIZER__PROVIDER="stub"

uv --offline --directory server run src/dev_observer/server/main.py




