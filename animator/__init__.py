import asyncio
import os

from flask import Flask
from flask_bootstrap import Bootstrap

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from . import auth, anilist, db, prediction, recommendations


def create_app(test_config=None):
    """Create and configure the app."""
    app = Flask(__name__, instance_relative_config=True)
    bootstrap = Bootstrap(app)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'anime.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(anilist.bp)
    app.register_blueprint(prediction.bp)
    app.register_blueprint(recommendations.bp)

    app.add_url_rule('/', endpoint='index')

    return app
