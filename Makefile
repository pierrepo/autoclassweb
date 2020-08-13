# Flask only app
# Available on port 5000
run: export FLASK_APP = flaskapp
run: export FLASK_DEBUG = 1
run:
	flask run
.PHONY: run


# Flask + gunicorn
# Available on port 5000
run-gunicorn:
	@test "${CONDA_DEFAULT_ENV}" = "autoclassweb" && echo "Conda env ${CONDA_DEFAULT_ENV} found" || { echo "not OK"; exit 1; }
	gunicorn --config gunicorn.py flaskapp:app
.PHONY: run-gunicorn


build-docker:
	docker build . -t autoclassweb
.PHONY: build-docker


# Flask + gunicorn in Docker
# Available on port 5000
run-docker:
	docker run -p 5000:5000 -v ${PWD}/config:/app/config -v ${PWD}/logs:/app/logs -v ${PWD}/results:/app/results autoclassweb:latest
.PHONY: run-docker