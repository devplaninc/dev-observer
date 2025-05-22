ROOT := $(shell git rev-parse --show-toplevel)
MAKEFLAGS += -j2

.PHONY: py-install npm-install generate-protos generate test test-py

py-install:
	uv --directory server sync

npm-install:
	cd web && npm install

generate-protos: py-install npm-install
	@scripts/gen_protos.sh

generate: generate-protos

test-py:
	uv --directory server run pytest

test: test-py
	# all tests executed


