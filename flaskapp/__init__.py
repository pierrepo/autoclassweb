import os
import sys
import shutil

from flask import Flask

app = Flask(__name__)

from flaskapp import routes

import autoclasswrapper as wrapper

os.environ["FLASK_RES_LINK"] = "True"
os.environ["FLASK_RES_MAIL"] = "False"

#  set Flask base directory
os.environ["FLASK_HOME"] = os.getcwd()
print("FLASK_HOME is {}".format(os.environ["FLASK_HOME"]))


# search autoclass executable in path
autoclass_path = shutil.which("autoclass")
if autoclass_path:
    print("autoclass found in {}".format(autoclass_path))
else:
    print("autoclass not found in path!")
    print("Exiting autoclassweb")
    sys.exit(1)


# load user Parameters
#config.read_ini("autoclassweb.ini")

# set config
app.config.from_pyfile('flaskapp.cfg')
#app.config.from_object('TestingConfig')
if "MAX_JOB" not in app.config:
    app.config["MAX_JOB"] = psutil.cpu_count() - 1
    print("MAX JOB defined as {}".format(app.config["MAX_JOB"]))
