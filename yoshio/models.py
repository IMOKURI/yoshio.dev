from datetime import datetime
import flask_login as fl
import sqlalchemy as sql
import sqlalchemy.orm as sqlo
from werkzeug.security import generate_password_hash, check_password_hash

from yoshio import db


class User(db.Model, fl.UserMixin):
    __tablename__ = 'users'

    lineid = sql.Column(sql.String(128), primary_key=True)
    username = sql.Column(sql.Unicode(128))
    _password = sql.Column(sql.String(128))

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        if password:
            password = password.strip()
        self._password = generate_password_hash(password)

    password_descriptor = property(_get_password, _set_password)
    password = sqlo.synonym('_password', descriptor=password_descriptor)

    def check_password(self, password):
        password = password.strip()
        if not password:
            return False
        return check_password_hash(self.password, password)

    @classmethod
    def auth(cls, query, lineid, password):
        user = query(cls).filter(cls.lineid == lineid).first()
        if user is None:
            return None, False
        return user, user.check_password(password)

    def get_id(self):
        return self.lineid


class WorkingHours(db.Model):
    __tablename__ = 'working_hours'

    whid = sql.Column(
        sql.Integer,
        default=0,
        primary_key=True,
        autoincrement=True
    )
    lineid = sql.Column(
        sql.String(128),
        sql.ForeignKey('users.lineid', onupdate='CASCADE', ondelete='CASCADE'),
        index=True
    )
    action = sql.Column(sql.Unicode(128))
    date = sql.Column(sql.DATETIME, default=datetime.now, nullable=False)
    sqlite_autoincrement = True


def init():
    db.create_all()
