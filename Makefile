run: export FLASK_APP = flaskapp
run:
	flask run
.PHONY: run

run-gunicorn:
	@test "${CONDA_DEFAULT_ENV}" = "autoclassweb" && echo "Conda env ${CONDA_DEFAULT_ENV} found" || { echo "not OK"; exit 1; }
	gunicorn --config gunicorn.conf flaskapp:app
.PHONY: run-gunicorn
