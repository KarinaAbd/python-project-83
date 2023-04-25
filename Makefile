PORT ?= 8000

install:
	poetry install

all-checks: lint check test

lint:
	poetry run flake8 page_analyzer

check:
	poetry check

test:
	poetry run pytest

dev:
	poetry run flask --app page_analyzer:app --debug run

start:
	poetry run gunicorn --workers=5 --bind=0.0.0.0:$(PORT) page_analyzer:app

database: db-create schema-load

db-create:
	createdb page_analyzer || echo 'skip'

schema-load:
	psql page_analyzer < database.sql

connect:
	psql page_analyzer
