from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from linebot import LineBotApi, WebhookHandler

from yoshio import config


app = Flask(__name__, instance_relative_config=True)

config.apply_to(app)

line_bot_api = LineBotApi(app.config['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(app.config['CHANNEL_SECRET'])

db = SQLAlchemy(app)

from yoshio import home, working_hours
app.register_blueprint(home.bp)
app.register_blueprint(working_hours.bp)


@app.errorhandler(404)
def error_not_found(error):
    return render_template('errors/404.html'), 404
