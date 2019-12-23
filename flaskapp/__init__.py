import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import sys

from dotenv import load_dotenv
from flask import Flask

app = Flask(__name__)

# Redefine logger.
from flask.logging import default_handler
# Clean default Flask logger.
app.logger.removeHandler(default_handler)
# Create a logging formatter.
formatter = logging.Formatter("%(asctime)s :: %(levelname)-8s :: %(module)s - %(message)s",
                                datefmt="%Y-%m-%d %H:%M:%S")
# Create a stream handler.
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
# Create a file handler.
file_handler = RotatingFileHandler("logs/flaskapp.log",
                                   mode="a",
                                   maxBytes=10000,
                                   backupCount=1)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
# Attach handlers to logger.
app.logger.addHandler(stream_handler)
app.logger.addHandler(file_handler)

#  set Flask base directory
os.environ["FLASK_HOME"] = os.getcwd()
app.logger.info("FLASK_HOME is {}".format(os.environ["FLASK_HOME"]))

# Set app configuration.
# First: try to find user config file.
config_file_name = "config/autoclassweb.cfg"
config_file_path = Path(os.environ["FLASK_HOME"]) / config_file_name
if config_file_path.exists():
    app.logger.info(f"Reading configuration in {config_file_name}")
    load_dotenv(dotenv_path=config_file_path, verbose=True)
else:
    app.logger.warning(f"Cannot find config file {config_file_name}")
    app.logger.warning("Default configuration is used!")
# Second: load default configuration
# config module must be loaded after user config file
import config
app.config.from_object(config.CreateConfig)
app.config["VERSION"] = "1.1.0"
app.logger.info(f"AutoClassWeb version: {app.config['VERSION']}")


from flaskapp import routes
