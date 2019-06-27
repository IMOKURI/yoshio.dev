from flask import Blueprint, render_template


bp = Blueprint('home', __name__)


@bp.route('/')
def index():
    return render_template(
        'pages/index.html',
        date='2019/4/16'
    )
