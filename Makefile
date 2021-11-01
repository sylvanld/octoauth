include .env.local

##@ Development

help: ## Show this help message and exit
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

$(VENV_PATH):
	virtualenv -p python3.8 $(VENV_PATH)

install: $(VENV_PATH) ## Install dev. dependencies in virtualenv
	$(VENV_PATH)/bin/pip install -r requirements/dev.txt

serve: $(VENV_PATH) ## Run dev. server with hot reload
	ENVIRONMENT=development $(VENV_PATH)/bin/uvicorn --factory octoauth.webapp:OctoAuthASGI --port 7000 --reload

clean: $(VENV_PATH) ## Remove useless files, and clean git branches
	git checkout main && git fetch -p && LANG=en_US git branch -vv | awk '/: gone]/{print $$1}' | xargs git branch -D
	find . -type d -name "__pycache__" | xargs rm -rf
	rm -rf site/ build/ public/ .pytest_cache/ *.sqlite

format: $(VENV_PATH) ## Format code, sort import and remove useless vars/imports
	# remove all unused imports
	$(VENV_PATH)/bin/autoflake -ir octoauth/ tests/ --remove-all-unused-imports --ignore-init-module-imports
	# sort imports
	$(VENV_PATH)/bin/isort octoauth/ tests/
	# format code
	$(VENV_PATH)/bin/black octoauth/ tests/

lint: $(VENV_PATH) ## Run pylint to check code quality
	$(VENV_PATH)/bin/pylint octoauth/ tests/

test: $(VENV_PATH) ## Run project automated tests
	$(VENV_PATH)/bin/python -m pytest tests/ -v

##@ Configuration

# path to the PKI used in JWT encoding

assets:
	mkdir -p assets

keygen: assets ## Generate public/private key pair used in JWT encoding in assets/ folder
	openssl genrsa -out assets/private-key.pem 2048
	openssl rsa -in assets/private-key.pem -outform PEM -pubout -out assets/public-key.pem
