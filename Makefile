default: help


run: export FLASK_APP = flaskapp:app ## Run autoclassweb (flask app) on port 5000
run: export FLASK_DEBUG = 1
run:
	flask run
.PHONY: run


run-gunicorn:  ## Run autoclassweb with gunicorn (port 5000)
	@test "${CONDA_DEFAULT_ENV}" = "autoclassweb" && echo "Conda env ${CONDA_DEFAULT_ENV} found" || { echo "not OK"; exit 1; }
	gunicorn --config gunicorn.py flaskapp:app
.PHONY: run-gunicorn


docker-build:  ## Build Docker image
	docker build . -t autoclassweb
.PHONY: docker-build


docker-run:  ## Run autoclassweb + gunicorn with Docker container (port 5000)
	docker run --rm --name autoclassweb -p 5000:5000 -v ${PWD}/config:/app/config -v ${PWD}/logs:/app/logs -v ${PWD}/results:/app/results autoclassweb:latest gunicorn --config /app/gunicorn.py flaskapp:app
.PHONY: docker-run


docker-clean:  ## Clean Docker images
	docker image prune --all --force
.PHONY: docker-clean


help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help
