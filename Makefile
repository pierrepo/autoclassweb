.PHONY: run run-gunicorn

run:
	pipenv run flask run

run-gunicorn:
	pipenv run gunicorn --config gunicorn.conf flaskapp:app
