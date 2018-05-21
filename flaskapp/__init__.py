import os
import sys

from flask import Flask

app = Flask(__name__)

#  set Flask base directory
os.environ["FLASK_HOME"] = os.getcwd()
print("FLASK_HOME is {}".format(os.environ["FLASK_HOME"]))

# set config
import config
app.config.from_object(config.CreateConfig)

from flaskapp import routes
