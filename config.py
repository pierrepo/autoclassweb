import logging
import os
import psutil
import uuid

import autoclasswrapper as wrapper

class CreateConfig():
    """Create Flask app configuration.

    Combine global environnement variables with local parameters.
    Environnement variables are usually defined in the .env file.
    """

    def format_true_false(env, default=""):
        """Format env variable to True / False.
        """
        content = os.environ.get(env, default)
        if content.upper() in ["T", "TRUE"]:
            os.environ[env] = "True"
            return True
        else:
            os.environ[env] = "False"
            return False

    # Catch Flask logger.
    logger = logging.getLogger("flaskapp")

    # No error found so far...
    FLASK_INIT_ERROR = ""

    # FLASK_ENV
    # default is 'production'
    os.environ["FLASK_ENV"] = os.environ.get("FLASK_ENV", "production")

    # FLASK_RESULTS_ARE_PUBLIC
    FLASK_RESULTS_ARE_PUBLIC = format_true_false("FLASK_RESULTS_ARE_PUBLIC",
                                                 "True")
    logger.info(f"FLASK_RESULTS_ARE_PUBLIC: {FLASK_RESULTS_ARE_PUBLIC}")

    # FLASK_RESULTS_BY_EMAIL
    FLASK_RESULTS_BY_EMAIL = format_true_false("FLASK_RESULTS_BY_EMAIL",
                                               "False")
    logger.info(f"FLASK_RESULTS_BY_EMAIL: {FLASK_RESULTS_BY_EMAIL}")

    if FLASK_RESULTS_ARE_PUBLIC == False \
      and FLASK_RESULTS_BY_EMAIL == False:
        FLASK_INIT_ERROR = ("FLASK_RESULTS_ARE_PUBLIC "
                            "and FLASK_RESULTS_BY_EMAIL "
                            "cannot be undefined or False simultaneously")

    # if FLASK_RESULTS_BY_EMAIL is True,
    # at least MAIL_SERVER_URL and MAIL_PORT should be defined
    if FLASK_RESULTS_BY_EMAIL:
        if os.environ.get("FLASK_SERVER_URL", "") == "":
            FLASK_INIT_ERROR = ("FLASK_SERVER_URL environnement variable "
                                "is not defined.")
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
        logger.info(f"MAIL_USE_TLS: {MAIL_USE_TLS}")

    # FLASK_MAX_JOBS
    if ("FLASK_MAX_JOBS" not in os.environ) \
      or (not os.environ["FLASK_MAX_JOBS"].isdigit()):
        FLASK_MAX_JOBS = psutil.cpu_count() - 1
    else:
        FLASK_MAX_JOBS = int(os.environ["FLASK_MAX_JOBS"])
    logger.info(f"FLASK_MAX_JOBS: {FLASK_MAX_JOBS}")

    # FLASK_JOB_TIMEOUT
    if ("FLASK_JOB_TIMEOUT" not in os.environ) \
      or (not os.environ["FLASK_JOB_TIMEOUT"].isdigit()):
        FLASK_JOB_TIMEOUT = 24
    else:
        FLASK_JOB_TIMEOUT = int(os.environ["FLASK_JOB_TIMEOUT"])
    logger.info(f"FLASK_JOB_TIMEOUT: {FLASK_JOB_TIMEOUT}")

    # FLASK_RESULTS_DURATION
    if ("FLASK_RESULTS_DURATION" not in os.environ) \
      or (not os.environ["FLASK_RESULTS_DURATION"].isdigit()):
        FLASK_RESULTS_DURATION = 30
    else:
        FLASK_RESULTS_DURATION = int(os.environ["FLASK_RESULTS_DURATION"])
    logger.info(f"FLASK_RESULTS_DURATION: {FLASK_RESULTS_DURATION}")

    # Search AutoClass C executable
    AUTOCLASSC_VERSION = wrapper.get_autoclass_version()
    AUTOCLASSC_PATH = wrapper.search_autoclass_in_path()
    if not AUTOCLASSC_VERSION:
        FLASK_INIT_ERROR = "Cannot find/run AutoClass C executable."

    # Print and store autoclasswrapper version
    AUTOCLASSWRAPPER_VERSION = wrapper.__version__
    logger.info(f"AutoClassWrapper version: {AUTOCLASSWRAPPER_VERSION}")
    

    # internal parameters
    if "SECRET_KEY" not in os.environ:
        logger.info("No SECRET_KEY found in env. Generating.")
    SECRET_KEY = os.environ.get("SECRET_KEY", str(uuid.uuid4()))
    RESULTS_FOLDER = os.path.join(os.environ["FLASK_HOME"], "results")
    JOB_NAME_LENGTH = 6
