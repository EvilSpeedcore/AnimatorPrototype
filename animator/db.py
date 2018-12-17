import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


class DBController:

    @staticmethod
    def get_connection():
        db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES,
                isolation_level=None,
                timeout=20)
        db.row_factory = sqlite3.Row
        return db

    @staticmethod
    def update(query, args):
        db = DBController.get_connection()
        db.execute(query, args)
        db.commit()
        db.close()

    @staticmethod
    def query(query, args, is_one):
        db = DBController.get_connection()
        result = db.execute(query, args).fetchone() if is_one else db.execute(query, args).fetchall()
        db.close()
        return result


def close_db(e=None):

    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = DBController.get_connection()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('initdb')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')