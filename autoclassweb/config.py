class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    UPLOAD_FOLDER="tmp"
    SECRET_KEY="1234"
    AUTOCLASS_PATH="bin/autoclass"
    MAX_JOB="4"
    JOB_NAME_LENGTH = 8
    JOB_PASSWD_LENGTH = 8


class TestingConfig(BaseConfig):
    """Testing configuration"""
    DEBUG = True
    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False