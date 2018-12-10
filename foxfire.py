import click
import os

from flask.cli import with_appcontext
from flask.cli import AppGroup

from app import create_app


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
db2_cli = AppGroup(
    'db2', help="Perform (extended) database operations."
)


def _clear():
    from app import models, db

    click.echo('Clearing data...')
    models.User.query.delete()
    models.Application.query.delete()
    models.Task.query.delete()
    models.Notification.query.delete()
    db.session.commit()


def _seed():
    import defaults
    from app import models, db

    click.echo('Seeding data...')

    user = models.User(
        username='John Doe',
        email='john.doe@example.com',
        company='ACME Inc.',
        password='S3cret!!',
        confirmed=True,
    )
    db.session.add(user)

    app = models.Application(
        appname='openf1-demo-app',
        description='python demo application.',
        aid=defaults.aid,
        pubkey=defaults.pubkey,
        key=defaults.key,
        fingerprint=defaults.fingerprint,
        owner=user,
    )
    db.session.add(app)

    task = models.Task(
        id=1,
        application=app,
        complete=True,
    )
    db.session.add(task)

    db.session.commit()


@db2_cli.command()
@with_appcontext
def clean():
    """Clean and re-populate db tables with test data."""
    _clear()
    _seed()


@db2_cli.command()
@with_appcontext
def clear():
    """Clear data from application db tables."""
    _clear()


@db2_cli.command()
@with_appcontext
def seed():
    """Seed application db tables with test data."""
    _seed()


app.cli.add_command(db2_cli)
