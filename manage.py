from flask_script import Manager
from autoclassweb import app, forms, model
import autoclasswrapper as wrapper 

import os

os.environ["FLASK_HOME"] = os.getcwd()

manager = Manager(app)


if __name__ == '__main__':
    manager.run()
    # host = '0.0.0.0'