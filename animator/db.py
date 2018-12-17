from flask import g
import pyodbc

CONNECTION_STRING = 'Driver={ODBC Driver 17 for SQL Server};Server=tcp:animator.database.windows.net,1433;Database=anime;Uid=Bamboocha@animator;Pwd=Qjcvsylsh1;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'


def init_app(app):
    app.teardown_appcontext(close_db)


class DBController:

    connection = pyodbc.connect(CONNECTION_STRING)
    cursor = connection.cursor()

    @staticmethod
    def update(query, args=()):

        DBController.cursor.execute(query, args)
        DBController.connection.commit()

    @staticmethod
    def query(query, args=(), is_one=False):
        DBController.cursor.execute(query, args)
        return DBController.cursor.fetchone() if is_one else DBController.cursor.fetchall()


def close_db(e=None):

    db = g.pop('db', None)

    if db is not None:
        db.close()

