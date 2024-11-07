.DEFAULT_GOAL := help
.PHONY: install check pytest pylint bandit style black isort help

install: ## Install/Upgrade all dependencies in editable mode
	pip install --upgrade -e '.[core,service,dev]'

check: pytest pylint pyright bandit ## Run pytest, pylint, pyright and bandit

pytest: ## Execute unit tests with pytest
	python -m pytest -s

pylint: ## Check code smells with pylint
	python -m pylint --exit-zero src

pyright: ## Check types
	python -m pyright

bandit: ## Check securty smells with bandit
	python -m bandit -c pyproject.toml -r src

style: black isort ## Run black and isort

black: ## Auto-format python code using black
	python -m black src

isort: ## Auto-format python code using isort
	python -m isort src

help: # Run `make help` to get help on the make commands
	@echo "\033[36mAvailable commands:\033[0m"
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
