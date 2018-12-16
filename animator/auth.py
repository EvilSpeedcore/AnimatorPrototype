import asyncio
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from animator.db import DBController


bp = Blueprint('auth', __name__, url_prefix='/auth')
loop = asyncio.get_event_loop()


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
        elif DBController.query(
                loop,
                """
                SELECT id FROM user WHERE username = ?
                """,
                (username, ), is_one=True) is not None:
            error = 'User {} is already registered.'.format(username)
        if error is None:
            DBController.update(
                loop,
                """
                INSERT INTO user (username, password) VALUES (?, ?)
                """,
                (username, generate_password_hash(password)))
            return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = DBController.query(
            loop,
            """
            SELECT * FROM user WHERE username = ?
            """,
            (username, ), is_one=True)
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
        g.user = DBController.query(
            loop,
            """
            SELECT * FROM user WHERE id = ?
            """,
            (user_id, ), is_one=True)


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
