import os

# gunicorn config file
# see :
# http://docs.gunicorn.org/en/stable/configure.html
# http://docs.gunicorn.org/en/stable/settings.html

bind = '0.0.0.0:%i' % int(os.getenv('PORT', 5000))
workers = 4
errorlog = '-'
accesslog = '-'
#loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'debug')
