import os


def apply_to(app):
    """Apply configurations"""

    app.config.from_mapping(
        # following parameter should be set in instance config
        # SECRET_KEY='snoopy',
        # CHANNEL_ACCESS_TOKEN='',
        # CHANNEL_SECRET='',

        # store the database in the instance folder
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'working_hours.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=True,
    )

    app.config.from_pyfile('config.py', silent=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
