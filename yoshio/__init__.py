from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('yoshio.config')
db = SQLAlchemy(app)

import yoshio.views
