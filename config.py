import os
import rq

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


def unquote(s):
    return s.strip()[1:-1]


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = False
    LOG_TO_STDOUT = os.environ.get("LOG_TO_STDOUT")
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_SUBJECT_PREFIX = "[openf1]"
    MAIL_SENDER = "openf1 admin <admin@openf1.com>"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or None
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD") or None

    @staticmethod
    def init_app(app):
        from redis import Redis
        app.redis = Redis.from_url(os.environ.get("REDIS_URL") or "redis://")
        app.task_queue = rq.Queue("foxfire-tasks", connection=app.redis)

    @staticmethod
    def version():
        with open('VERSION', 'r') as f:
            _, v = f.read().split('=')
        return {'version': unquote(v)}


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")
    MAIL_SERVER = os.environ.get("MAIL_SERVER") or "localhost"
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 8025)

    @staticmethod
    def version():
        with open('VERSION', 'r') as f:
            _, v = f.read().split('=')
        sha = os.environ.get('GIT_SHA')
        if sha:
            suffix = '+{}'.format(sha[0:4])
        else:
            suffix = '+dev'
        return {'version': unquote(v) + suffix}


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or \
        "sqlite://"
    WTF_CSRF_ENABLED = False

    @classmethod
    def init_app(cls, app):
        from fakeredis import FakeRedis as Redis
        app.redis = Redis.from_url(os.environ.get("REDIS_URL") or "redis://")
        app.task_queue = rq.Queue(
            "foxfire-tasks", connection=app.redis)

    @staticmethod
    def version():
        with open('VERSION', 'r') as f:
            _, v = f.read().split('=')
        return {'version': unquote(v) + '-rc'}


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "data.sqlite")

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class HerokuConfig(ProductionConfig):
    LOG_TO_STDOUT = True

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuConfig,

    'default': DevelopmentConfig
}
