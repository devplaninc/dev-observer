#!/usr/bin/env bash

set -ex
set -o pipefail

root=$(git rev-parse --show-toplevel)
mkdir -p "${root}"/server/src/dev_observer/api/
mkdir -p "${root}"/web/packages/api/src/pb/

PROTO_FILES=$(find proto -name "*.proto" | sed 's|^proto/||')

uv --directory "$root"/server run python -m grpc_tools.protoc \
  -I "${root}/proto"  \
  --python_out=./src/ \
  --grpc_python_out=./src/ \
  --pyi_out=./src/ \
  --experimental_allow_proto3_optional \
  ${PROTO_FILES}

find "${root}"/server/src/dev_observer/api/ -type d -exec touch {}/__init__.py \;

protoc \
  -I "${root}/proto"  \
  --plugin=./web/node_modules/.bin/protoc-gen-ts_proto \
  --ts_proto_out=web/packages/api/src/pb \
  --ts_proto_opt=globalThisPolyfill=true,unrecognizedEnum=false,oneof=unions-value,outputServices=nice-grpc,outputServices=generic-definitions,useExactTypes=false \
  ${PROTO_FILES}
