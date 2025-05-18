ROOT := $(shell git rev-parse --show-toplevel)
MAKEFLAGS += -j2

.PHONY: py-install generate-protos generate test test-py

py-install:
	uv --directory server sync

generate-protos: py-install
	@scripts/gen_protos.sh

generate: generate-protos

test-py:
	uv --directory server run pytest

test: test-py
	# all tests executed


