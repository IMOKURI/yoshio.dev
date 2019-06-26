from sqlalchemy import *
from werkzeug.security import generate_password_hash, check_password_hash

from yoshio import db


class User(db.Model):
    userid = Column(Integer, primary_key=True)
    username = Column(Unicode(128))
    lineid = Column(String(128), unique=True, index=True)
    password_hash = Column(String(128))

    def __init__(self, userid, username, lineid, password):
        self.userid = userid
        self.username = username
        self.lineid = lineid
        self.set_password(password)

    def __repr__(self):
        return '<User userid={} lineid={!r}>'.format(self.userid, self.lineid)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class WorkingHours(db.Model):
    lineid = Column(
        String(128),
        ForeignKey('user.lineid', onupdate='CASCADE', ondelete='CASCADE'),
        primary_key=True
    )
    date = Column(DATETIME)
    action = Column(String(128))


def init():
    db.create_all()
