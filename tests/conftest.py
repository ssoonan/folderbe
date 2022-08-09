from app import create_app
from app.config import Config
from app.db import init_db, get_db

import pytest


class TestConfig(Config):
    TESTING = True


@pytest.fixture
def app():
    app = create_app(config_class=TestConfig)
    with app.app_context():
        init_db()
    yield app