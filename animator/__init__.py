import asyncio
import os

from celery import Celery
from flask import Flask
from flask_bootstrap import Bootstrap

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

from . import auth, anilist, db, prediction, recommendations


def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app(test_config=None):
    """Create and configure the app."""
    app = Flask(__name__, instance_relative_config=True)
    bootstrap = Bootstrap(app)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'anime.sqlite'),
        CELERY_BROKER_URL='redis://localhost:6379',
        CELERY_RESULT_BACKEND='redis://localhost:6379'
    )
    celery = make_celery(app)

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
