# autoclass-web

A web app to run autoclass clustering.

# Setup

1. Install virtualenv

    ```
    $ sudo pip3 install pipenv
    ```

2. Create virtual environment

    ```
    $ pipenv --three
    ```

3. Install requirements

    ```
    $ pipenv install pandas flask flask-wtf psutil chardet
    ```

# Usage

```
$ export FLASK_APP=flaskapp/app.py
$ pipenv run flask run
```

or quicker:

```
make run
```
