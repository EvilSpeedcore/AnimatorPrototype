import asyncio
import json
import io

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import jikanpy.exceptions
import pandas as pd

from . import parser
from animator.db import DBController
from animator.auth import login_required


bp = Blueprint('anilist', __name__)
loop = asyncio.get_event_loop()


@bp.route('/update', methods=('GET', 'POST'))
@login_required
def update():
    return redirect(url_for('anilist.create'))


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        mal_username = request.form['mal_username']
        if not mal_username:
            flash('MyAnimeList username is required.')
        else:
            try:
                user = parser.MALUser(mal_username)
            except jikanpy.exceptions.APIException:
                flash('Invalid username.')
            else:
                set_constructor = parser.DataSetConstructor(user.anime_list)
                data = json.dumps(set_constructor.create_data_set())
                DBController.update(
                    loop,
                    """
                    INSERT OR REPLACE INTO profile(mal_username, profile_id, url, list)
                    VALUES (?, ?, ?, ?);
                    """,
                    (mal_username, g.user['id'], 'None', data)
                )
                return redirect(url_for('prediction.index'))
    return render_template('list_creation/create_list.html')


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Please, select file to upload.')
            return redirect(url_for('anilist.create'))
        file = request.files.get('file')
        if file:
            stream = io.BytesIO(file.read())
            data = pd.read_csv(stream).to_json()
            DBController.update(
                loop,
                """
                INSERT OR REPLACE INTO profile(mal_username, profile_id, url, list)
                VALUES (?, ?, ?, ?);        
                """,
                ('None', g.user['id'], 'None', data)
            )
            return redirect(url_for('prediction.index'))