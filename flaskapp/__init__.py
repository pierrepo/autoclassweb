import os
import sys
import shutil

from flask import Flask

app = Flask(__name__)

#  set Flask base directory
os.environ["FLASK_HOME"] = os.getcwd()
print("FLASK_HOME is {}".format(os.environ["FLASK_HOME"]))


# load config from env variables
from flaskapp import tools
tools.read_env_config()


from flaskapp import routes

import autoclasswrapper as wrapper
print("autoclasswrapper version: ", wrapper.__version__)
autoclass_path = wrapper.search_autoclass_in_path()
if not autoclass_path:
    os.environ["FLASK_INIT_ERROR"] = "Cannot find autoclass-c executable in PATH."


# set config
app.config.from_pyfile('flaskapp.cfg')
#app.config.from_object('TestingConfig')
if "MAX_JOB" not in app.config:
    app.config["MAX_JOB"] = psutil.cpu_count() - 1
    print("MAX JOB defined as {}".format(app.config["MAX_JOB"]))
