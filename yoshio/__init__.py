import logging
import logging.handlers

from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from linebot import LineBotApi, WebhookHandler

from yoshio import config


app = Flask(__name__, instance_relative_config=True)

log_handler = logging.handlers.RotatingFileHandler("/var/log/yoshio/yoshio.log", "a+", maxBytes=3000, backupCount=5)
log_handler.setLevel(logging.INFO)
log_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s'))
app.logger.addHandler(log_handler)

app.logger.info('Start up.')

config.apply_to(app)

line_bot_api = LineBotApi(app.config['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(app.config['CHANNEL_SECRET'])

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.blueprint_login_views = {
    'working_hours': '/working_hours/login'
}

from yoshio.models import User


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('home.index'))
    # TODO: It is better login view by blueprint.


from yoshio import home, working_hours
app.register_blueprint(home.bp)
app.register_blueprint(working_hours.bp)


@app.errorhandler(404)
def error_not_found(error):
    return render_template('errors/404.html'), 404
