PYTHON ?= python
COMPOSE ?= docker compose -f infra/docker/docker-compose.yml

.PHONY: help install lint format test bench up down logs migrate seed

help:
	@echo "make install   - install local dev deps"
	@echo "make lint      - ruff + isort check + mypy"
	@echo "make format    - black + isort"
	@echo "make test      - pytest"
	@echo "make bench     - run benchmark suite"
	@echo "make up/down   - docker compose up/down"
	@echo "make migrate   - apply migrations"
	@echo "make seed      - seed deterministic benchmark data"

install:
	pip install -r requirements/local.txt

lint:
	ruff check .
	isort --check-only .
	mypy --no-error-summary . || true

format:
	black .
	isort .

test:
	pytest

bench:
	pytest -m benchmark --benchmark-only

up:
	$(COMPOSE) up --build -d

down:
	$(COMPOSE) down -v

logs:
	$(COMPOSE) logs -f --tail=200

migrate:
	$(PYTHON) manage.py migrate

seed:
	$(PYTHON) manage.py seed_benchmark_data
