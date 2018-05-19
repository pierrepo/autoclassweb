.PHONY: clean run run-gunicorn

clean:
	rm -rf tmp/20*.*.*

run:
	pipenv run flask run

run-gunicorn:
	pipenv run gunicorn --config gunicorn-conf.py flaskapp:app
