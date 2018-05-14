import os
import configparser


# read config parameters
def read_ini(ininame):
    """Read config parameters for the web app

    Parameters
    ----------
    ininame : str
    Name of ini file containing parameters
    """
    if not os.path.exists(ininame):
        os.environ["FLASK_CONFIG"] = "False"
        os.environ["FLASK_RES_LINK"] = "True"
        os.environ["FLASK_RES_MAIL"] = "False"
        return 1
    os.environ["FLASK_CONFIG"] = "True"
    config = configparser.ConfigParser()
    config.read(ininame)
    # results section
    os.environ["FLASK_RES_LINK"] = str(config["results"].getboolean("link", False))
    os.environ["FLASK_RES_MAIL"] = str(config["results"].getboolean("mail", True))
    # mail section
    os.environ["FLASK_MAIL_HOST"] = config["mail"].get("host", "")
    os.environ["FLASK_MAIL_PORT"] = str(config["mail"].getint("port", 0))
    os.environ["FLASK_MAIL_SSL"] = str(config["mail"].getboolean("SSL", True))
    os.environ["FLASK_MAIL_LOGIN"] = config["mail"].get("login", "")
    os.environ["FLASK_MAIL_PASSWORD"] = config["mail"].get("password", "")
    os.environ["FLASK_MAIL_SENDER"] = config["mail"].get("sender", os.environ["FLASK_MAIL_LOGIN"])
