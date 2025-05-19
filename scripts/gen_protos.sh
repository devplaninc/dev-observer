#!/usr/bin/env bash

set -ex
set -o pipefail

root=$(git rev-parse --show-toplevel)
mkdir -p "${root}"/server/src/dev_observer/api/
mkdir -p "${root}"/web/src/pb/

PROTO_FILES=$(find proto -name "*.proto" | sed 's|^proto/||')

uv --directory "$root"/server run python -m grpc_tools.protoc \
  -I "${root}/proto"  \
  --python_out=./src/dev_observer/api \
  --grpc_python_out=./src/dev_observer/api \
  --pyi_out=./src/dev_observer/api \
  ${PROTO_FILES}

find "${root}"/server/src/dev_observer/api/ -type d -exec touch {}/__init__.py \;

protoc \
  -I "${root}/proto"  \
  --plugin=./web/node_modules/.bin/protoc-gen-ts_proto \
  --ts_proto_out=web/src/pb \
  --ts_proto_opt=unrecognizedEnum=false,oneof=unions-value,outputServices=nice-grpc,outputServices=generic-definitions,useExactTypes=false \
  ${PROTO_FILES}
