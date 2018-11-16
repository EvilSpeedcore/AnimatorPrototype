import asyncio
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from animator.db import get_db, query_db, update_db


bp = Blueprint('auth', __name__, url_prefix='/auth')
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif loop.run_until_complete(query_db(
                """
                SELECT id FROM user WHERE username = ?
                """,
                (username, ), one=True
        )) is not None:
            error = 'User {} is already registered.'.format(username)
        if error is None:
            loop.run_until_complete(update_db(
                """
                INSERT INTO user (username, password) VALUES (?, ?)
                """,
                (username, generate_password_hash(password))))
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = loop.run_until_complete(query_db(
            """
            SELECT * FROM user WHERE username = ?'
            """,
            (username, ), one=True))
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        flash(error)
    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?',
            (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
