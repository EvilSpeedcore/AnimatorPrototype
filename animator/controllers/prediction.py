import json
from pathlib import Path
from urllib.parse import urlsplit

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from jikanpy.exceptions import APIException
import pandas as pd

from animator import db, learning, parser
from animator.controllers.auth import login_required
from animator.models.models import Profile, Recommendations


bp = Blueprint('prediction', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
    user_id = session.get('user_id')
    if user_id is None:
        return redirect(url_for('auth.login'))
    data_set = Profile.query.filter_by(profile_id=user_id).first()
    data = pd.DataFrame(json.loads(data_set.list)) if data_set else pd.DataFrame()
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
            profile = Profile.query.filter_by(profile_id=g.user.id).first()
            anime_list = json.loads(profile.list)
            model = learning.ModelConstructor(anime_list).model
            if not model:
                flash('Number of completed titles is too damn low!')
            else:
                predictor = learning.Predictor(model)
                prediction, train_accuracy, test_accuracy = predictor.make_prediction(anime_page_data)
                if prediction:
                    recommendation = Recommendations.query.filter_by(title=anime_page_data.title).first()
                    if not recommendation:
                        recommendation = Recommendations(title=anime_page_data.title,
                                                         anime_type=anime_page_data.type,
                                                         episodes=anime_page_data.episodes,
                                                         studio=anime_page_data.studio,
                                                         src=anime_page_data.source,
                                                         genre=anime_page_data.genre,
                                                         score=anime_page_data.score,
                                                         synopsis=anime_page_data.synopsis,
                                                         image_url=anime_page_data.image_url,
                                                         url=anime_page_data.url,
                                                         profile_id=g.user.id)
                        db.session.add(recommendation)
                        db.session.commit()
                return render_template('prediction/prediction.html',
                                       anime_page_data=anime_page_data,
                                       prediction=prediction,
                                       train_accuracy=train_accuracy,
                                       test_accuracy=test_accuracy)
    return render_template('prediction/prediction.html')
