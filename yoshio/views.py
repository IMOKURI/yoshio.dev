from flask import render_template

from yoshio import app, db
from yoshio.models import User, WorkingHours


@app.route('/')
def index():
    return render_template(
        'pages/index.html',
        date='2019/4/16'
    )


@app.errorhandler(404)
def error_not_found(error):
    return render_template('errors/404.html'), 404
