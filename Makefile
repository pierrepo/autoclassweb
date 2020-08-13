# Flask only app
# Available on port 5000
run: export FLASK_APP = flaskapp
run: export FLASK_DEBUG = 1
run:
	flask run
.PHONY: run


# Flask + gunicorn app
# Available on port 5000
run-gunicorn:
	@test "${CONDA_DEFAULT_ENV}" = "autoclassweb" && echo "Conda env ${CONDA_DEFAULT_ENV} found" || { echo "not OK"; exit 1; }
	gunicorn --config gunicorn.py flaskapp:app
.PHONY: run-gunicorn


docker-build:
	docker build . -t autoclassweb
.PHONY: docker-build