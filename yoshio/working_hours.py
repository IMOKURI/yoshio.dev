from flask import Blueprint, render_template, request, redirect, flash, session
import flask_login as fl

from yoshio import db
from yoshio.models import User


import imp
try:
    imp.find_module('pysnooper')
    import pysnooper
except ImportError:
    pass


bp = Blueprint('working_hours', __name__, url_prefix="/working_hours")


@bp.route('/')
def index():
    return render_template('pages/wh_index.html')


@pysnooper.snoop()
@bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        lineid = request.form['lineid']
        password = request.form['password']

        user, authenticated = User.auth(
            db.session.query,
            lineid,
            password
        )

        if authenticated:
            fl.login_user(user, remember=True)
            flash('Login successfull!', 'success')
            return redirect('/working_hours/dashboard')

        flash('Login failed...', 'fail')

    return render_template('pages/wh_login.html')


@bp.route('/dashboard', methods=['GET', 'POST'])
@fl.login_required
def dashboard():
    if request.method == 'POST':
        # TODO
        pass

    return render_template('pages/wh_dashboard.html')


@bp.route('/register', methods=['GET', 'POST'])
@fl.login_required
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

        # TODO: Error handling
        db.session.add(user)
        db.session.commit()
        flash('Added new user!')

    return render_template('pages/wh_register.html')


@bp.route('/logout')
@fl.login_required
def logout():
    user = fl.current_user
    fl.logout_user()
    flash('Logout successfull! See you, {}'.format(user.username))
    return redirect('/working_hours')
