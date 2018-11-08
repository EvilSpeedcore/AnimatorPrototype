import json
import io

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import pandas as pd

from app.auth import login_required
from app.db import get_db

from . import main
from . import constructor

UPLOAD_FOLDER = r'C:\Program Files'
bp = Blueprint('prediction', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
    #  TODO: Load user data set. In html if there is no data set - propose to load one.
    #  TODO: If there is data set, propose to view it and make a prediction.
    #  TODO: If not user logged, show register page.
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('auth.login'))
    data_set = get_db().execute(
        """
        SELECT p.list 
        FROM profile p 
        INNER JOIN user u
        ON p.id = u.id
        WHERE p.profile_id = ? 
        """, (user_id, )
    ).fetchone()
    data = pd.DataFrame(json.loads(data_set['list'])).head(5) if data_set else pd.DataFrame()
    return render_template('prediction/index.html', data_set=data)


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
    return render_template('prediction/create.html')


@bp.route('/predict', methods=('GET', 'POST'))
@login_required
def predict():
    if request.method == 'POST':
        anime_url = request.form['anime_url']
        if not anime_url:
            flash('Please, enter anime URL.')
        else:
            anime_page_data = main.parse_anime_page(anime_url)
            anime_list = get_db().execute(
                """
                SELECT list
                FROM profile
                WHERE profile_id = ?
                """,
                (str(g.user['id']))
            ).fetchone()[0]

            anime_list = json.loads(anime_list)

            feature_constructor = constructor.ModelConstructor(anime_list)
            feature_constructor.create_model()
            prediction, train_accuracy, test_accuracy = feature_constructor.predict(anime_page_data)
            if prediction:
                #  TODO: Write to data base.
                get_db().execute(
                    """
                    INSERT OR IGNORE INTO recommendations(profile_id,title,episodes,studio,src,genre,score)
                    VALUES(?,?,?,?,?,?,?)
                    """,
                    (str(g.user['id']),
                     anime_page_data['Title'],
                     anime_page_data['Episodes'],
                     anime_page_data['Studios'],
                     anime_page_data['Source'],
                     anime_page_data['Genres'],
                     anime_page_data['Score'])
                )
                get_db().commit()

            return render_template('prediction/make.html',
                                   anime_page_data=anime_page_data,
                                   prediction=prediction,
                                   train_accuracy=train_accuracy,
                                   test_accuracy=test_accuracy)
        return render_template('prediction/make.html')
    return render_template('prediction/make.html')


@bp.route('/update', methods=('GET', 'POST'))
@login_required
def update():
    return render_template('prediction/create.html')


@bp.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Please, select file to upload.')
            return render_template('prediction/create.html')
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return render_template('prediction/create.html')
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