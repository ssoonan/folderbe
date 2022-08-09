from flask_bootstrap import Bootstrap5
from flask import Flask

from .config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.secret_key = "12r#!sd21Q"
    app.config.from_object(config_class)

    bootstrap = Bootstrap5()

    bootstrap.init_app(app)

    from . import main
    app.register_blueprint(main.bp)

    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import db
    db.helper.init_app(app)

    return app