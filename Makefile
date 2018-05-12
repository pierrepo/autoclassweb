.PHONY: clean


clean:
	rm -rf tmp/20*.*.*

run:
	FLASK_APP=autoclassweb; pipenv run flask run
