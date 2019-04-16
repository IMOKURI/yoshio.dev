#!/usr/bin/env python

"""
Source code for https://yoshio.dev
"""

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template(
        'pages/index.html',
        date='2019/4/16'
    )


@app.errorhandler(404)
def error_not_found(error):
    return render_template('errors/404.html'), 404


if __name__ == '__main__':
    app.run()
