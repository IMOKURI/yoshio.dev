import os


def apply_to(app, test_config):
    """Apply configurations"""

    env = os.environ.get('FLASK_ENV') or 'Dev'

    if env == 'Prod':
        debug = False
    else:
        debug = True

    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='snoopy',

        # store the database in the instance folder
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'working_hours.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=True,

        DEBUG=debug
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)
