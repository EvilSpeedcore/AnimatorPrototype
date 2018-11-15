#  TODO: Think about using OrderedDict in project just in case.
#  TODO: Change order of anime list columns on index page.
#  TODO: Update (clean up) requirements.txt
import json
from pathlib import Path
from urllib.parse import urlsplit

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from jikanpy.exceptions import APIException
import pandas as pd

from animator.auth import login_required
from animator.db import get_db
from . import learning, parser


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
        WHERE p.profile_id = ?
        """,
        (str(user_id))
    ).fetchone()
    data = pd.DataFrame(json.loads(data_set['list'])) if data_set else pd.DataFrame()
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
            anime_id = Path(urlsplit(anime_url).path).parts[2]
            anime_page_data = parser.AnimePageInfo(anime_id)
        except (IndexError, APIException):
            flash(message)
        else:
            #  TODO: Use session.get(user_id) instead of g.user['id']?. See recommendations.py
            anime_list = get_db().execute(
                """
                SELECT list
                FROM profile
                WHERE profile_id = ?
                """,
                (str(g.user['id']))
            ).fetchone()[0]

            anime_list = json.loads(anime_list)
            model = learning.ModelConstructor(anime_list).model
            if not model:
                flash('Number of completed titles is too damn low!')
            else:
                predictor = learning.Predictor(model)
                prediction, train_accuracy, test_accuracy = predictor.make_prediction(anime_page_data)
                if prediction:
                    get_db().execute(
                        """
                        INSERT OR IGNORE INTO recommendations(profile_id,title,anime_type,episodes,studio,src,genre,score)
                        VALUES(?,?,?,?,?,?,?,?)
                        """,
                        (str(g.user['id']),
                         anime_page_data.title,
                         anime_page_data.type,
                         anime_page_data.episodes,
                         anime_page_data.studio,
                         anime_page_data.source,
                         anime_page_data.genre,
                         anime_page_data.score)
                    )
                    get_db().commit()
                return render_template('prediction/prediction.html',
                                       anime_page_data=anime_page_data,
                                       prediction=prediction,
                                       train_accuracy=train_accuracy,
                                       test_accuracy=test_accuracy)
    return render_template('prediction/prediction.html')
