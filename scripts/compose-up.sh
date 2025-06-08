#!/usr/bin/env bash

set -ex
set -o pipefail

root=$(git rev-parse --show-toplevel)

cd "$root"/docker
docker compose --env-file compose_env/.env.local --env-file "$root"/server/.env.local.secrets up
