import asyncio
import json
import io

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import pandas as pd

from . import parser
from animator.db import DBController
from animator.auth import login_required


bp = Blueprint('anilist', __name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


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
            #  Works file when pressed first on loading page.
            #  If pressed after no file error, there is no error and request is /upload, not /create.
            error = 'MyAnimeList username is required.'
        if error is not None:
            flash(error)
        else:
            user = parser.MALUser(mal_username)
            set_constructor = parser.DataSetConstructor(user.anime_list)
            data = json.dumps(set_constructor.create_data_set())
            DBController.update(
                """
                INSERT OR REPLACE INTO profile(mal_username, profile_id, url, list)
                VALUES (?, ?, ?, ?);
                """,
                (mal_username, g.user['id'], 'None', data), loop=loop
            )
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
        if not file.filename:
            flash('No selected file.')
            return render_template('list_creation/create_list.html')
        if file:
            stream = io.BytesIO(file.read())
            data = pd.read_csv(stream).to_json()
            DBController.update(
                """
                INSERT OR REPLACE INTO profile(mal_username, profile_id, url, list)
                VALUES (?, ?, ?, ?);        
                """,
                ('None', g.user['id'], 'None', data), loop=loop
            )
            return redirect(url_for('prediction.index'))