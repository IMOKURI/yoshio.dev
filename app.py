#!/usr/bin/env python

"""
Source code for https://yoshio.dev
"""

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def welcome():
    return render_template(
        'index.html',
        title='Welcome to yoshio.dev!',
        date='2019/4/16'
    )


if __name__ == '__main__':
    app.run()
