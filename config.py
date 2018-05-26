import os
import uuid
import psutil
import autoclasswrapper as wrapper

class CreateConfig():
    """Create Flask app configuration

    Combine global environnement variables with local parameters.
    Environnement variables are usually defined in the .env file.
    """

    def format_true_false(env, default=""):
        """Format env variable to True / False
        """
        content = os.environ.get(env, default)
        if content.upper() in ["T", "TRUE"]:
            os.environ[env] = "True"
            return True
        else:
            os.environ[env] = "False"
            return False

    # not error so far...
    FLASK_INIT_ERROR = ""

    # FLASK_ENV
    # default is 'production'
    os.environ["FLASK_ENV"] = os.environ.get("FLASK_ENV", "production")

    # FLASK_RESULTS_ARE_PUBLIC
    FLASK_RESULTS_ARE_PUBLIC = format_true_false("FLASK_RESULTS_ARE_PUBLIC",
                                                 "False")
    print("FLASK_RESULTS_ARE_PUBLIC is", FLASK_RESULTS_ARE_PUBLIC)

    # FLASK_RESULTS_BY_EMAIL
    FLASK_RESULTS_BY_EMAIL = format_true_false("FLASK_RESULTS_BY_EMAIL",
                                               "False")
    print("FLASK_RESULTS_BY_EMAIL is", FLASK_RESULTS_BY_EMAIL)

    if FLASK_RESULTS_ARE_PUBLIC == False \
      and FLASK_RESULTS_BY_EMAIL == False:
        FLASK_INIT_ERROR = ("FLASK_RESULTS_ARE_PUBLIC "
                            "and FLASK_RESULTS_BY_EMAIL "
                            "cannot be undefined or False simultaneously")

    # if FLASK_RESULTS_BY_EMAIL is True,
    # at least MAIL_SERVER and MAIL_PORT should be defined
    if FLASK_RESULTS_BY_EMAIL:
        if os.environ.get("MAIL_SERVER", "") == "":
            FLASK_INIT_ERROR = ("MAIL_SERVER environnement variable "
                                "is not defined.")
        if not os.environ.get("MAIL_PORT", "").isdigit():
            FLASK_INIT_ERROR = ("MAIL_PORT environnement variable "
                                "is not defined or is not a valid number.")

    # if FLASK_RESULTS_BY_EMAIL is True,
    # MAIL_USE_TLS shoud be True or False
    if FLASK_RESULTS_BY_EMAIL:
        MAIL_USE_TLS = format_true_false("MAIL_USE_TLS",
                                         "False")

    # FLASK_MAX_JOBS
    if ("FLASK_MAX_JOBS" not in os.environ) \
      or (not os.environ["FLASK_MAX_JOBS"].isdigit()):
        FLASK_MAX_JOBS = psutil.cpu_count() - 1
    else:
        FLASK_MAX_JOBS = int(os.environ["FLASK_MAX_JOBS"])
    print("FLASK_MAX_JOBS:", FLASK_MAX_JOBS)

    # FLASK_JOB_TIMEOUT
    if ("FLASK_JOB_TIMEOUT" not in os.environ) \
      or (not os.environ["FLASK_JOB_TIMEOUT"].isdigit()):
        FLASK_JOB_TIMEOUT = 3600
    else:
        FLASK_JOB_TIMEOUT = int(os.environ["FLASK_JOB_TIMEOUT"])
    print("FLASK_JOB_TIMEOUT:", FLASK_JOB_TIMEOUT)


    # autoclass-c executable
    print("autoclasswrapper version: ", wrapper.__version__)
    autoclass_path = wrapper.search_autoclass_in_path()
    if not autoclass_path:
        FLASK_INIT_ERROR = "Cannot find autoclass-c executable in PATH."


    # internal parameters
    if "SECRET_KEY" not in os.environ:
        print("No SECRET_KEY found in env. Generating.")
    SECRET_KEY = os.environ.get("SECRET_KEY", str(uuid.uuid4()))
    RESULTS_FOLDER = os.path.join(os.environ["FLASK_HOME"], "results")
    JOB_NAME_LENGTH = 8
    # time to check is simulation are still alive
    # in seconds 
    JOB_ALIVE = 180
