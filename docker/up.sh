#!/usr/bin/env bash

set -ex
set -o pipefail

env_name=${1:-default}

working_dir="$(pwd)"
certs_path="$working_dir"/certs
mkdir -p "$certs_path"

rm -f .env.__combined__
cat .env .env."${env_name}" > .env.__combined__

cat <<EOF >> .env.__combined__

SERVER_CONFIG_PATH=${working_dir}/observer_config.toml
SERVER_SECRETS_PATH=${working_dir}/.env.${env_name}.secrets
SERVER_ENV_PATH=${working_dir}/.env.__combined__
CERTS_PATH=${certs_path}

EOF

rm -rf dev-observer

git clone --filter=blob:none --no-checkout https://github.com/devplaninc/dev-observer.git
cd dev-observer

# Enable sparse checkout
git sparse-checkout init --cone

# Set the folder you want
git sparse-checkout set docker

# Checkout
git checkout main

cd docker

docker compose pull
docker compose --profile ssl down --remove-orphans --volumes
docker ps

docker compose \
  --profile ssl \
  --env-file "$working_dir"/.env.__combined__ \
  --env-file "$working_dir"/.env."${env_name}".secrets \
  up -d --wait --wait-timeout 120

docker ps
docker compose logs --tail=50
