from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from linebot import LineBotApi, WebhookHandler

from yoshio import config


app = Flask(__name__, instance_relative_config=True)

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
