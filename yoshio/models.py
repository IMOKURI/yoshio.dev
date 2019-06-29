import sqlalchemy as sql
from sqlalchemy.sql.expression import func

from yoshio import db


class User(db.Model):
    __tablename__ = 'users'

    lineid = sql.Column(sql.String(128), primary_key=True)
    username = sql.Column(sql.Unicode(128))

    @classmethod
    def auth(cls, query, lineid):
        user = query(cls).filter(cls.lineid == lineid).first()
        if user is None:
            return None, False
        return user, True


class WorkingHours(db.Model):
    __tablename__ = 'working_hours'
    __table_args__ = {'sqlite_autoincrement': True}

    whid = sql.Column(
        sql.Integer,
        primary_key=True,
        autoincrement=True
    )
    lineid = sql.Column(
        sql.String(128),
        sql.ForeignKey('users.lineid', onupdate='CASCADE', ondelete='CASCADE'),
        index=True
    )
    action = sql.Column(sql.Unicode(128))
    date = sql.Column(sql.types.DateTime(), server_default=func.now())


def init():
    db.create_all()
