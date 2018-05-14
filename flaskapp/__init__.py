import os
import sys
import shutil

from flask import Flask

app = Flask(__name__)

#  set Flask base directory
os.environ["FLASK_HOME"] = os.getcwd()
print("FLASK_HOME is {}".format(os.environ["FLASK_HOME"]))


# load user Parameters
from flaskapp import tools
tools.read_ini(os.path.join(os.environ["FLASK_HOME"], "autoclassweb.ini"))

from flaskapp import routes

import autoclasswrapper as wrapper


# search autoclass executable in path
autoclass_path = shutil.which("autoclass")
if autoclass_path:
    print("autoclass found in {}".format(autoclass_path))
else:
    print("autoclass not found in path!")
    print("Exiting autoclassweb")
    sys.exit(1)




# set config
app.config.from_pyfile('flaskapp.cfg')
#app.config.from_object('TestingConfig')
if "MAX_JOB" not in app.config:
    app.config["MAX_JOB"] = psutil.cpu_count() - 1
    print("MAX JOB defined as {}".format(app.config["MAX_JOB"]))
