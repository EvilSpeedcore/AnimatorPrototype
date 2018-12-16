import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
import aiosqlite


def init_app(app):
    init_db()
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


class DBController:

    @staticmethod
    async def _update_db(query, args):
        async with aiosqlite.connect(current_app.config['DATABASE'],
                                     detect_types=sqlite3.PARSE_DECLTYPES) as db:
            db.row_factory = sqlite3.Row
            await db.execute(query, args)
            await db.commit()

    @staticmethod
    async def _query_db(query, args, is_one):
        async with aiosqlite.connect(current_app.config['DATABASE'],
                                     detect_types=sqlite3.PARSE_DECLTYPES) as db:
            db.row_factory = sqlite3.Row
            cursor = await db.execute(query, args)
            result = await cursor.fetchone() if is_one else await cursor.fetchall()
            return result

    @staticmethod
    def update(loop, query, args=()):
        loop.run_until_complete(DBController._update_db(query, args))

    @staticmethod
    def query(loop, query, args=(), is_one=False):
        return loop.run_until_complete(DBController._query_db(query, args, is_one))


def close_db(e=None):

    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    #  TODO: Replace with async version?
    db = sqlite3.connect(current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('initdb')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
