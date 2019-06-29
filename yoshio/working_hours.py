# -*- coding: utf-8 -*-

from collections import defaultdict

from flask import (
    Blueprint,
    abort,
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
    username, authenticated = User.auth(
        db.session.query,
        lineid,
    )

    if authenticated:
        wh_data = db.session.query(WorkingHours).filter(WorkingHours.lineid == lineid).all()

        wh_data_by_date = defaultdict(list)
        for d in wh_data:
            date = d.date.strftime('%Y/%m/%d')
            wh_data_by_date[date].append(d)

        wh_table = []
        for date in wh_data_by_date:
            begin = ''
            end = ''
            for d in wh_data_by_date[date]:
                time = d.date.strftime('%H:%M')
                if d.action == 'begin':
                    begin = time
                elif d.action == 'end':
                    end = time
            wh_table.append({'date': date, 'begin': begin, 'end': end})

        return render_template(
            'pages/wh_dashboard.html',
            username=username,
            wh_table=wh_table
        )

    return redirect(url_for('working_hours.index'))


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

    if action in ['begin', 'end']:
        wh_data = WorkingHours(
            lineid=lineid,
            action=action,
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
