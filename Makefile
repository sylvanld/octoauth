include .env.local

##@ Development

help: ## Show this help message and exit
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

$(VIRTUALENV_PATH):
	virtualenv -p python3.8 $(VIRTUALENV_PATH)

install: $(VIRTUALENV_PATH) ## Install dev. dependencies in virtualenv
	$(VIRTUALENV_BIN)/pip install -r requirements/dev.txt

serve: $(VIRTUALENV_PATH) ## Run dev. server with hot reload
	$(VIRTUALENV_BIN)/uvicorn --factory octoauth.webapp:OctoAuthASGI --port 7000 --reload

clean: $(VIRTUALENV_PATH) ## Format code, sort import and remove useless vars/imports
	# remove all unused imports
	$(VIRTUALENV_BIN)/autoflake -ir octoauth/ tests/ --remove-all-unused-imports --ignore-init-module-imports
	# sort imports
	$(VIRTUALENV_BIN)/isort octoauth/ tests/
	# format code
	$(VIRTUALENV_BIN)/black octoauth/ tests/

lint: $(VIRTUALENV_PATH) ## Run pylint to check code quality
	$(VIRTUALENV_BIN)/pylint octoauth/ tests/

test: $(VIRTUALENV_PATH) ## Run project automated tests
	$(VIRTUALENV_BIN)/python -m pytest tests/ -v

##@ Git tools

git-prune: $(VIRTUALENV_PATH) ## Remove useless files, and clean git branches
	git checkout main && git fetch -p && LANG=en_US git branch -vv | awk '/: gone]/{print $$1}' | xargs git branch -D
	find . -type d -name "__pycache__" | xargs rm -rf
	rm -rf site/ build/ public/ .pytest_cache/ *.sqlite

##@ Configuration

assets:
	mkdir -p assets

keygen: assets ## Generate public/private key pair used in JWT encoding in assets/ folder
	openssl genrsa -out assets/private-key.pem 2048
	openssl rsa -in assets/private-key.pem -outform PEM -pubout -out assets/public-key.pem
