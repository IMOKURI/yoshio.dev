# -*- coding: utf-8 -*-

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from linebot.exceptions import InvalidSignatureError
import linebot.models as lm

from yoshio import db, line_bot_api, handler
from yoshio.models import User, WorkingHours


bp = Blueprint('working_hours', __name__, url_prefix="/working_hours")


@bp.route('/')
def index():
    return render_template('pages/wh_index.html')


@bp.route('/<lineid>')
def dashboard(lineid):
    user, authenticated = User.auth(
        db.session.query,
        lineid,
    )

    if authenticated:
        username = db.session.query(User).filter(User.lineid == lineid).first()
        wh_data = db.session.query(WorkingHours).filter(WorkingHours.lineid == lineid).all()

        return render_template(
            'pages/wh_dashboard.html',
            username=username,
            wh_data=wh_data
        )

    return redirect(url_for('working_hours.index'))


@bp.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError as e:
        logger.exceptions(e)
        abort(400)
    logger.info('Connection test OK.')
    return 'OK'


@handler.add(lm.FollowEvent)
def handle_follow(event):
    lineid = event.source.user_id
    profile = line_bot_api.get_profile(lineid)
    username = profile.display_name

    user = User(
        username=username,
        lineid=lineid
    )

    # TODO: Error handling
    db.session.add(user)
    db.session.commit()

    msg = u'下のボタンから勤怠を登録してね。勤怠記録はこちらを参照してね。 https://yoshio.dev/working_hours/{}'.format(lineid)

    line_bot_api.reply_message(
        event.reply_token,
        lm.TextSendMessage(text=msg)
    )


@handler.add(lm.PostbackEvent)
def handle_postback(event):
    lineid = event.source.user_id

    if 'begin' in event.postback.data:
        action = 'begin'
        msg = u'出勤時刻を記録しました。今日も頑張って！'
    elif 'end' in event.postback.data:
        action = 'end'
        msg = u'退勤時刻を記録しました。お疲れ様でした！'
    elif 'display' in event.postback.data:
        action = 'display'
        msg = u'勤怠記録はこちらを参照してね。 https://yoshio.dev/working_hours/{}'.format(lineid)
    else:
        action = None
        msg = u'おや！？'

    if action in ['bebin', 'end']:
        wh_data = WorkingHours(
            lineid=lineid,
            action=action,
            date=event.timestamp
        )

        # TODO: Error handling
        db.session.add(wh_data)
        db.session.commit()

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
