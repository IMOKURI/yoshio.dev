# -*- coding: utf-8 -*-

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
)
import flask_login as fl

from linebot.exceptions import InvalidSignatureError
import linebot.models as lm

from yoshio import db, line_bot_api, handler
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
            flash(u'ログインしました(^^)', 'success')
            return redirect('/working_hours/dashboard')

        flash(u'ログインに失敗しました。。。', 'fail')

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
    flash(u'ログアウトしました。(^^)ﾉｼ')
    return redirect('/working_hours')


@bp.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(lm.FollowEvent)
def handle_follow(event):
    uid = event.source.user_id
    profile = line_bot_api.get_profile(uid)
    name = profile.display_name

    # TODO: Register user to DB
    pass


@handler.add(lm.PostbackEvent)
def handle_postback(event):
    uid = event.source.user_id
    action = event.postback.data

    msg = event.timestamp

    line_bot_api.reply_message(
        event.reply_token,
        lm.TextSendMessage(text=msg)
    )


@handler.add(lm.MessageEvent, message=lm.TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        lm.TextSendMessage(text=event.message.text)
    )
