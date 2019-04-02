from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config


app = Flask(__name__, instance_relative_config=True)
bootstrap = Bootstrap(app)
app.config.from_object(Config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from animator.controllers import anilist, auth, prediction, recommendations

app.register_blueprint(auth.bp)
app.register_blueprint(anilist.bp)
app.register_blueprint(prediction.bp)
app.register_blueprint(recommendations.bp)

app.add_url_rule('/', endpoint='index')