ROOT := $(shell git rev-parse --show-toplevel)
MAKEFLAGS += -j2

.PHONY: py-install npm-install generate-protos generate test test-py

start-local-pg:
	@scripts/local-pg.sh

py-install:
	uv --directory server sync

npm-install:
	cd web && npm install

generate-protos: py-install npm-install
	@scripts/gen_protos.sh

generate: generate-protos

test-py:
	uv --directory server run pytest

new-migration: start-local-pg
	uv --directory server run alembic revision --autogenerate -m "init tables"

migration-new:
ifndef MNAME
	$(error MSG is not set. Please run: make new-migration MNAME="migration name")
endif
	uv --directory server run alembic revision --autogenerate -m "$(MNAME)"

migration-apply:
	uv --directory server run alembic upgrade head

dev-server:
	@cd server && uv run scripts/dev/main.py

local-server:
	@cd server && uv run scripts/local/main.py

dev-web: npm-install
	@cd web/apps/dev-observer && npm run dev

local-compose:
	@scripts/compose-up.sh

test: test-py
	# all tests executed


