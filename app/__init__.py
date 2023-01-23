import os
from flask_bootstrap import Bootstrap5
from flask import Flask

from .config import config
from .oauth_api import pretty_date


def create_app(config_name='development'):
    app = Flask(__name__)
    used_config = config[config_name]
    app.config.from_object(used_config)
    app.secret_key = used_config.SESSION_KEY

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


app = create_app(os.getenv('FLASK_CONFIG'))