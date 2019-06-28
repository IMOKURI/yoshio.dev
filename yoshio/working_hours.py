from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
)
import flask_login as fl

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
import linebot.models as lm

from yoshio import db
from yoshio.models import User


import imp
try:
    imp.find_module('pysnooper')
    import pysnooper
except ImportError:
    pass


bp = Blueprint('working_hours', __name__, url_prefix="/working_hours")

line_bot_api = LineBotApi(current_app.config['CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(current_app.config['CHANNEL_SECRET'])


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


@bp.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(lm.MessageEvent, message=lm.TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        lm.TextSendMessage(text=event.message.text)
    )
