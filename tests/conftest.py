from app import create_app
from app.config import Config, DaoConfig
from app.db import init_db, get_db

import pytest


class TestConfig(Config):
    TESTING = True


@pytest.fixture
def app():
    app = create_app(config=TestConfig)
    with app.app_context():
        init_db()
    yield app


@pytest.fixture
def app_for_dao():
    app = create_app(config=DaoConfig)