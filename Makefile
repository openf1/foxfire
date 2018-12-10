.PHONY: clean clean-build clean-pyc clean-test help

.DEFAULT_GOAL := help

define BROWSER_PYSCRIPT
import os, webbrowser, sys

from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
    match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
    if match:
        target, help = match.groups()
        print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc clean-test

clean-build: ## remove build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	rm -rf logs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -rf  {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '*.pyo' -exec rm -rf {} +
	find . -name '*~' -exec rm -rf {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test: ## remove test and coverage artifacts
	rm -rf .tox/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache
	rm -rf pytestdebug.log

lint: ## check style with flake8
	flake8 app tests foxfire.py run-worker.py config.py --ignore W605

test: ## run tests quickly with the default Python
	pytest

test-all: lint coverage ## run all tests (linting, unittests, coverage) 

coverage: ## check code coverage quickly with the default Python
	@$(MAKE) clean > /dev/null
	coverage run --source app -m pytest 
	coverage report -m --fail-under=100

coverage-codacy: coverage ## upload code quality report to codacy
	coverage xml
	python-codacy-coverage -r coverage.xml

coverage-html: ## generate and show html code coverage report
ifeq (,$(wildcard .coverage))
	@$(MAKE) coverage
else
	coverage html
	$(BROWSER) htmlcov/index.html
endif

db: db-init db-migrate db-upgrade ## create new db and its migration scripts

db-init: ## init new db
	flask db init

db-migrate: ## generate db migration scripts
	flask db migrate

db-upgrade: ## migrate and upgrade db
	flask db upgrade

db-clean: ## clear and seed data to db
	flask db2 clear
	flask db2 seed

db-clear: ## clear db tables
	flask db2 clear

db-seed: ## add seed data to db
	flask db2 seed

rq-worker: ## launch rq worker
	python -u run-worker.py

mailer: ## launch simple Python mail server daemon
	scripts/smtpd

server: ## launch flask server with default environment
	scripts/server
