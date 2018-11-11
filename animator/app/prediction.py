import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import pandas as pd
import requests.exceptions

from app.auth import login_required
from app.db import get_db
from . import constructor, main


bp = Blueprint('prediction', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
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


@bp.route('/predict', methods=('GET', 'POST'))
@login_required
def predict():
    if request.method == 'POST':
        anime_url = request.form['anime_url']
        if not anime_url:
            message = 'Please, enter anime URL.'
        else:
            message = 'Incorrect URL. Valid example: https://myanimelist.net/anime/457/Mushishi'
        try:
            anime_page_data = main.parse_anime_page(anime_url)
        except (AttributeError, requests.exceptions.MissingSchema):
            flash(message)
        else:
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
            return render_template('prediction/prediction.html',
                                   anime_page_data=anime_page_data,
                                   prediction=prediction,
                                   train_accuracy=train_accuracy,
                                   test_accuracy=test_accuracy)
    return render_template('prediction/prediction.html')
