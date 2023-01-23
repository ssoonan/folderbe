import os


class DefaultConfig:
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "test")
    SESSION_KEY = os.environ.get("SESSION_KEY", "123RT$!es^")


class DaoConfig(DefaultConfig):  # DAO 로직 테스트만을 위한 config
    pass


class AppConfig(DefaultConfig):  # flask app을 위한 config
    CLIENT_ID = os.environ.get("CLIENT_ID")
    CLIENT_SECRET = os.environ.get("CLIENT_SECRET")  # TODO: 흩어져있는 config 환경변수 합치기
    SESSION_KEY = os.environ.get("SESSION_KEY", "123RT$!es^")


class ProductionConfig(AppConfig):
    pass


config = {
    'development': AppConfig,
    'production': ProductionConfig
}