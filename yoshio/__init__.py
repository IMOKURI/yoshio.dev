from flask import Flask, render_template
from flask_login import LoginManager

from yoshio import config


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    config.apply_to(app, test_config)

    from yoshio.models import db

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.blueprint_login_views = {
        'working_hours': '/working_hours/login'
    }

    from yoshio import home, working_hours
    app.register_blueprint(home.bp)
    app.register_blueprint(working_hours.bp)

    @app.errorhandler(404)
    def error_not_found(error):
        return render_template('errors/404.html'), 404

    return app


app = create_app()
