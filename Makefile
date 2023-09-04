
.PHONY: run-server
run-server:
	poetry run python -m core.manage runserver


.PHONY: superuser
superuser:
	 poetry run python -m core.manage createsuperuser

.PHONY: install
install:
	poetry install

.PHONY: migrations
migrations:
	poetry run python -m core.manage makemigrations

.PHONY: migrate
migrate:
	poetry run python -m core.manage migrate

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall; poetry run pre-commit install

.PHONY: update
update: install migrate install-pre-commit ;

.PHONY: up-dependencies-only
up-dependencies-only:
	IF NOT EXIST .env (echo. > .env)
	docker-compose -f .docker-compose.dev.yml up --force-recreate db
