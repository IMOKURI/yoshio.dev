from datetime import datetime
from flask import Blueprint, render_template, request, redirect, session, url_for
import flask_login as fl
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sql
from werkzeug.security import generate_password_hash, check_password_hash


bp = Blueprint('working_hours', __name__, url_prefix="/working_hours")

db = SQLAlchemy()


class User(db.Model, fl.UserMixin):
    __tablename__ = 'users'

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
    __tablename__ = 'working_hours'

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


# @login_manager.user_loader
def user_loader(lineid):
    return User.query.filter_by(lineid=lineid).first()


@bp.route('/')
def index():
    return render_template('pages/wh_index.html')


@bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        lineid = request.form['lineid']
        password = request.form['password']

        user = db.session.query(User).filter_by(lineid=lineid).first()

        fl.login_user(user)
        session['is_login'] = True

        return redirect(url_for('working_hours.index'))

    return render_template('pages/wh_login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        lineid = request.form['lineid']
        password = request.form['password']

        user = User(
            username=username,
            lineid=lineid,
            password=password,
        )
        db.session.add(user)
        db.session.commit()


@bp.route('/logout')
@fl.login_required
def logout():
    user = fl.current_user
    msg = u'See you, {} (^^)/'.format(user.username)
    fl.logout_user()
    return msg
