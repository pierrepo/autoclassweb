.PHONY: clean


clean:
	rm -rf tmp/20*.*.*

run:
	export FLASK_APP=autoclassweb; pipenv run flask run

