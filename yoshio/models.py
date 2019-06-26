from datetime import datetime
import sqlalchemy as sql
from werkzeug.security import generate_password_hash, check_password_hash

from yoshio import db


class User(db.Model):
    lineid = sql.Column(sql.String(128), primary_key=True)
    username = sql.Column(sql.Unicode(128))
    password_hash = sql.Column(sql.String(128))

    def __init__(self, lineid, username, password):
        self.lineid = lineid
        self.username = username
        self.set_password(password)

    def __repr__(self):
        return '<User lineid={!r}>'.format(self.lineid)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class WorkingHours(db.Model):
    whid = sql.Column(
        sql.Integer,
        default=0,
        primary_key=True,
        autoincrement=True
    )
    lineid = sql.Column(
        sql.String(128),
        sql.ForeignKey('user.lineid', onupdate='CASCADE', ondelete='CASCADE'),
        index=True
    )
    action = sql.Column(sql.Unicode(128))
    date = sql.Column(sql.DATETIME, default=datetime.now, nullable=False)
    sqlite_autoincrement = True


def init():
    db.create_all()
