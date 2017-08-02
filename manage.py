from flask_script import Manager

from autoclassweb import app, forms, model, io


manager = Manager(app)


if __name__ == '__main__':
    manager.run()
    # host = '0.0.0.0'