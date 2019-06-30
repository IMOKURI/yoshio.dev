# -*- coding: utf-8 -*-

from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta

from pytz import timezone, utc

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
        now_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        first_date_of_this_month = now_date.replace(day=1)
        first_date_of_next_month = (first_date_of_this_month + relativedelta(months=1))

        wh_data = db.session.query(WorkingHours).filter(
            WorkingHours.lineid == lineid,
            WorkingHours.date.between(first_date_of_this_month, first_date_of_next_month)
        ).all()

        wh_data_by_date = {}
        for single_date in daterange(first_date_of_this_month, first_date_of_next_month):
            date = single_date.strftime('%Y/%m/%d (%a)')
            wh_data_by_date[date] = []

        for d in wh_data:
            date = d.date.replace(tzinfo=utc).astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d (%a)')
            wh_data_by_date[date].append(d)

        wh_table = []
        for date in wh_data_by_date:
            begin = ''
            end = ''
            for d in wh_data_by_date[date]:
                time = d.date.replace(tzinfo=utc).astimezone(timezone('Asia/Tokyo')).strftime('%H:%M')
                if d.action == 'begin':
                    begin = time
                elif d.action == 'end':
                    end = time
            wh_table.append({'date': date, 'begin': begin, 'end': end})

        wh_table.sort(key=lambda d: d['date'])

        return render_template(
            'pages/wh_dashboard.html',
            username=username,
            wh_table=wh_table
        )

    return redirect(url_for('working_hours.index'))


@bp.route('/<lineid>/last')
def dashboard_last(lineid):
    username, authenticated = User.auth(
        db.session.query,
        lineid,
    )

    if authenticated:
        now_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        first_date_of_this_month = now_date.replace(day=1)
        first_date_of_last_month = (first_date_of_this_month - relativedelta(months=1))

        wh_data = db.session.query(WorkingHours).filter(
            WorkingHours.lineid == lineid,
            WorkingHours.date.between(first_date_of_last_month, first_date_of_this_month)
        ).all()

        wh_data_by_date = {}
        for single_date in daterange(first_date_of_last_month, first_date_of_this_month):
            date = single_date.strftime('%Y/%m/%d (%a)')
            wh_data_by_date[date] = []

        for d in wh_data:
            date = d.date.replace(tzinfo=utc).astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d (%a)')
            wh_data_by_date[date].append(d)

        wh_table = []
        for date in wh_data_by_date:
            begin = ''
            end = ''
            for d in wh_data_by_date[date]:
                time = d.date.replace(tzinfo=utc).astimezone(timezone('Asia/Tokyo')).strftime('%H:%M')
                if d.action == 'begin':
                    begin = time
                elif d.action == 'end':
                    end = time
            wh_table.append({'date': date, 'begin': begin, 'end': end})

        wh_table.sort(key=lambda d: d['date'])

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


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)
