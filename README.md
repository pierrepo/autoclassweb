# autoclass-web

A web app to run autoclass clustering.

# Setup

1. Install pipenv

    ```
    $ pip3 install --user pipenv
    ```

2. Create virtual environment

    ```
    $ pipenv --three
    ```

3. Install requirements

    ```
    $ pipenv install
    ```

# Usage

```
$ export FLASK_APP=autoclassweb
$ pipenv run flask run
```

or quicker:
```
$ make run
```

autoclass-web in then accessible at <http://127.0.0.1:5000/>

Gunicorn can also be used:
```
$ pipenv run gunicorn -b localhost:8000 -w 4 flaskapp:app
```

autoclass-web in then accessible at <http://127.0.0.1:8000/>
