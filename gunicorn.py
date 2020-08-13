import os
import uuid

# gunicorn config file
# see :
# http://docs.gunicorn.org/en/stable/configure.html
# http://docs.gunicorn.org/en/stable/settings.html

bind = "0.0.0.0:{}".format(int(os.getenv('PORT', 5000)))
workers = 4
errorlog = "logs/gunicorn-error.log"
accesslog = "logs/gunicorn-access.log"
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')

# FLask SECRET_KEY must be the same for all workers
os.environ["SECRET_KEY"] = str(uuid.uuid4())
