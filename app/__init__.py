from flask_bootstrap import Bootstrap5
from flask import Flask

from .config import Config, AppConfig
from .oauth_api import pretty_date


def create_app(config: AppConfig = AppConfig):
    app = Flask(__name__)
    app.config.from_object(config)
    app.secret_key = config.SESSION_KEY

    bootstrap = Bootstrap5()

    bootstrap.init_app(app)

    from . import main
    app.register_blueprint(main.bp)

    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import db
    db.helper.init_app(app)

    app.jinja_env.globals.update(pretty_date=pretty_date)

    return app