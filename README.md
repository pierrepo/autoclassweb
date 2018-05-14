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

with gunicorn :
```
$ pipenv run gunicorn -b localhost:8000 -w 4 flaskapp:app
```
