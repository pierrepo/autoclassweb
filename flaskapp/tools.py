import os

def format_true_false_env(env):
    """Format env variable to True / False
    """
    var = os.environ[env]
    if var.upper() in ["T", "TRUE"]:
        return "True"
    elif var.upper() in ["F", "FALSE"]:
        return "False"
    else:
        return ""

# check config parameters
def read_env_config():
    """Read config from environnement variables

    Environnement variables are usually defined
    in the .env file.
    """
    # check existence
    for var in ["FLASK_RESULTS_ARE_PUBLIC", "FLASK_RESULTS_BY_EMAIL"]:
        if var not in os.environ:
            os.environ["FLASK_INIT_ERROR"] = \
                "{} environnement variable not defined.".format(var)
            return 1
    # check format
    for env in ["FLASK_RESULTS_ARE_PUBLIC", "FLASK_RESULTS_BY_EMAIL"]:
        var_formatted = format_true_false_env(env)
        if var_formatted:
            os.environ[env] = var_formatted
        else:
            os.environ["FLASK_INIT_ERROR"] = \
                "{} environnement variable should be True or False.".format(env)
            return 1
    # if FLASK_RESULTS_BY_EMAIL is True,
    # at least MAIL_SERVER and MAIL_PORT should be defined
    if os.environ["FLASK_RESULTS_BY_EMAIL"] == "True":
        for env in ["MAIL_SERVER", "MAIL_PORT"]:
            if env not in os.environ:
                os.environ["FLASK_INIT_ERROR"] = \
                    "{} environnement variable not defined.".format(env)
                return 1
        # and MAIL_PORT should not be empty
        if os.environ["MAIL_SERVER"] == "":
            os.environ["FLASK_INIT_ERROR"] = \
                "MAIL_SERVER environnement variable should not be empty."
            return 1
        # and MAIL_PORT should be a number
        if not os.environ["MAIL_PORT"].isdigit():
            os.environ["FLASK_INIT_ERROR"] = \
                "MAIL_PORT environnement variable should be a number."
            return 1
    return 0
