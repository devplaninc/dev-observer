#!/usr/bin/env bash

set -ex
set -o pipefail

root=$(git rev-parse --show-toplevel)

PG_DATA_PATH="$root/.bin/pg-data-local"
mkdir -p "${PG_DATA_PATH}"

PG_DATA_PATH=${PG_DATA_PATH} docker compose -f scripts/local-pg-docker-compose.yaml up --no-recreate --detach
