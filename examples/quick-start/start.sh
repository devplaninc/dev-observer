#!/usr/bin/env bash

set -e
set -o pipefail

# Check if GOOGLE_API_KEY environment variable is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Error: GOOGLE_API_KEY environment variable is not set."
    echo "Please set the GOOGLE_API_KEY environment variable before running this script."
    echo "You can set it by running: export GOOGLE_API_KEY=your_api_key_here"
    exit 1
fi

root=$(git rev-parse --show-toplevel)

script_dir=$(cd "$(dirname "$0")" && pwd)
app_data="$script_dir"/app_data
mkdir -p "$app_data"

export DEV_OBSERVER_CONFIG_FILE="${script_dir}"/config.toml
export DEV_OBSERVER__STORAGE__LOCAL__DIR="${app_data}"/storage
export DEV_OBSERVER__OBSERVATIONS__LOCAL__DIR="${app_data}"/observations
export DEV_OBSERVER__PROMPTS__LOCAL__DIR="${script_dir}"/prompts

cleanup() {
    echo "Shutting down processes..."
    kill $SERVER_PID $WEB_PID 2>/dev/null || true
    wait $SERVER_PID $WEB_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

export GRPC_DNS_RESOLVER=native
cd "$root"/server
uv run scripts/examples/init_quickstart_data/main.py

uv run src/dev_observer/server/main.py &
SERVER_PID=$!

cd "$root"
make dev-web &
WEB_PID=$!


echo "Both web and server started. Ctrl+C to exit"

wait $SERVER_PID $WEB_PID

