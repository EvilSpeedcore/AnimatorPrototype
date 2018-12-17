import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
import aioodbc

CONNECTION_STRING = 'Driver={ODBC Driver 17 for SQL Server};Server=tcp:animator.database.windows.net,1433;Database=anime;Uid=Bamboocha@animator;Pwd=Qjcvsylsh1;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


class DBController:

    @staticmethod
    async def _update_db(query, args, loop):
        async with aioodbc.create_pool(dsn=CONNECTION_STRING, loop=loop) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, args)
                    await conn.commit()

    @staticmethod
    async def _query_db(query, args, is_one, loop):
        async with aioodbc.create_pool(dsn=CONNECTION_STRING, loop=loop) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, args)
                    result = await cur.fetchone() if is_one else await cur.fetchall()
                    return result

    @staticmethod
    def update(loop, query, args=()):
        loop.run_until_complete(DBController._update_db(query, args, loop))

    @staticmethod
    def query(loop, query, args=(), is_one=False):
        return loop.run_until_complete(DBController._query_db(query, args, is_one, loop))


def close_db(e=None):

    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    #  TODO: Replace with async version?
    db = sqlite3.connect(current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    db.close()


@click.command('initdb')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
