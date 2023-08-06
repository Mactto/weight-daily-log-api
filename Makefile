.PHONY: all
all:


.PHONY: update_requirements
update_requirements:
	rm -f requirements.txt requirements-dev.txt
	pip-compile --generate-hashes --resolver=backtracking --strip-extras --no-header -o requirements.txt pyproject.toml
	pip-compile --generate-hashes --resolver=backtracking --strip-extras --no-header --extra dev -o requirements-dev.txt pyproject.toml

.PHONY: format
format:
	isort launcher.py app/ migration/ tests/
	black launcher.py app/ migration/ tests/
	flake8 launcher.py app/ migration/ tests/
	mypy launcher.py app/ migration/ tests/

.PHONY: check
check:
# wait the release of https://github.com/pyupio/safety/pull/451
	# safety check
	black --check launcher.py app/ migration/ tests/
	flake8 launcher.py app/ migration/ tests/
# exclude /migration from mypy
	mypy launcher.py app/ tests/
	bandit -ll -r launcher.py app/ migration/ tests/
# B608: hardcoded_sql_expressions
	bandit -ll -r -s B608 migration/

.PHONY: pre_commit
pre_commit:
	if [ ! -d .git ]; then echo ".git is not initialized"; exit 1; fi

	echo "#!/bin/sh\nmake check" > .git/hooks/pre-commit

	chmod -R 700 .git/hooks/pre-commit
