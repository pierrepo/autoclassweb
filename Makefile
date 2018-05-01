.PHONY: clean


clean:
	rm -rf tmp/20*.*.*

run:
	FLASK_APP=flaskapp/app.py; pipenv run flask run
