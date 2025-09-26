PACKAGE := laser_gates
PACKAGE_DIR := src/${PACKAGE}
SHELL := env PYTHON_VERSION=3.13 /bin/bash
.SILENT: install devinstall tools test run lint format
PYTHON_VERSION ?= 3.13

setup:
	curl -LsSf https://astral.sh/uv/install.sh | sh

install:
	uv python pin $(PYTHON_VERSION)
	uv sync --no-dev

devinstall:
	uv python pin $(PYTHON_VERSION)
	uv lock -extra devarc
	uv sync --extra devarc

tools:
	uv tool install ruff --force
	uv tool install ipython --force

test:
	uv run pytest

run: 
	uv run python game.py

lint:
	uv tool run ruff check -q

format:
	uv tool run ruff format

all: devinstall tools lint format test
