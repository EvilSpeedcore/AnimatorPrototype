import io

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import pandas as pd

from . import main
from app.db import get_db
from app.auth import login_required


bp = Blueprint('anilist', __name__)


@bp.route('/update', methods=('GET', 'POST'))
@login_required
def update():
    return redirect(url_for('anilist.create'))


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        mal_username = request.form['mal_username']
        error = None
        if not mal_username:
            error = 'MyAnimeList username is required.'
        if error is not None:
            flash(error)
        else:
            data = main.convert_anime_list_into_json(mal_username)
            record = get_db().execute(
                """
                SELECT *
                FROM profile
                WHERE profile_id = ?
                """,
                (str(g.user['id']))
            ).fetchone()
            if not record:
                get_db().execute(
                    """
                    INSERT INTO profile (mal_username, profile_id, url, list)
                    VALUES (?, ?, ?, ?)
                    """,
                    (mal_username, g.user['id'], 'None', data)
                )
                get_db().commit()
            else:
                get_db().execute(
                    """
                    UPDATE profile
                    SET list = ?
                    WHERE profile_id = ? 
                    """,
                    (data, g.user['id'])
                )
                get_db().commit()
            return redirect(url_for('prediction.index'))
    return render_template('list_creation/create_list.html')


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Please, select file to upload.')
            return render_template('list_creation/create_list.html')
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return render_template('list_creation/create_list.html')
        if file:
            a = io.BytesIO(file.read())
            b = pd.read_csv(a).to_json()
            record = get_db().execute(
                """
                SELECT *
                FROM profile
                WHERE profile_id = ?
                """,
                (str(g.user['id']))
            ).fetchone()
            if not record:
                get_db().execute(
                    """
                    INSERT INTO profile (mal_username, profile_id, url, list)
                    VALUES (?, ?, ?, ?)
                    """,
                    ('None', g.user['id'], 'None', b)
                )
                get_db().commit()
            else:
                get_db().execute(
                    """
                    UPDATE profile
                    SET list = ?
                    WHERE profile_id = ? 
                    """,
                    (b, g.user['id'])
                )
                get_db().commit()
            return redirect(url_for('prediction.index'))