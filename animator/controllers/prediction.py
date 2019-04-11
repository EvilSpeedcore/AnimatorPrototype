import concurrent.futures
import json
from pathlib import Path
import random
from urllib.parse import urlsplit

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from jikanpy.exceptions import APIException
import pandas as pd

from animator import db, learning, parser
from animator.controllers.auth import login_required
from animator.models.models import Recommendations, Profile, TopAnime


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
                try:
                    prediction, train_accuracy, test_accuracy = predictor.make_prediction(anime_page_data)
                except ValueError:
                    flash('Not enough data to make a prediction.')
                else:
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


def test(result):
    anime_url = result.url
    anime_id = Path(urlsplit(anime_url).path).parts[2]
    try:
        anime_page_data = parser.AnimePageInfo(anime_id)
    except (IndexError, APIException):
        return None
    else:
        return anime_page_data


@bp.route('/get_prediction', methods=('GET', 'POST'))
@login_required
def get_prediction():
    genres = list({row.genre for row in db.session.query(TopAnime).all()})
    types = list({row.anime_type for row in db.session.query(TopAnime).all()})
    sources = list({row.src for row in db.session.query(TopAnime).all()})
    genres.insert(0, 'None')
    types.insert(0, 'None')
    sources.insert(0, 'None')
    if request.method == 'GET':
        return render_template('prediction/get_prediction.html', genres=genres, types=types, sources=sources)
    elif request.method == 'POST':
        query = []
        selected_episodes = request.form['episodes_input']
        if selected_episodes:
            query.append(TopAnime.episodes == selected_episodes)
        selected_source = request.form['source-selection']
        if selected_source != 'None':
            query.append(TopAnime.src == selected_source)
        selected_type = request.form['type-selection']
        if selected_type != 'None':
            query.append(TopAnime.anime_type == selected_type)
        selected_genre = request.form['genre-selection']
        if selected_genre != 'None':
            query.append(TopAnime.genre == selected_genre)
        results = TopAnime.query.filter(*query).all()
        profile = Profile.query.filter_by(profile_id=g.user.id).first()
        if not profile:
            flash('You need to create anime list first.')
            return render_template('prediction/get_prediction.html', genres=genres, types=types, sources=sources)
        elif not results:
            flash('No titles were found.')
            render_template('prediction/get_prediction.html', genres=genres, types=types, sources=sources)
        if results:
            if len(results) > 10:
                results = random.sample(results, 10)
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                pages = [r for r in executor.map(test, results) if r is not None]
            profile = Profile.query.filter_by(profile_id=g.user.id).first()
            anime_list = json.loads(profile.list)
            model = learning.ModelConstructor(anime_list).model
            recommendations = []
            if not model:
                flash('Number of completed titles is too damn low!')
            else:
                predictor = learning.Predictor(model)
                for page in pages:
                    try:
                        prediction, train_accuracy, test_accuracy = predictor.make_prediction(page)
                        if prediction:
                            recommendations.append(page)
                    except ValueError:
                        pass
                if not recommendations:
                    flash('No recommendations for you this time.')
                else:
                    objects = []
                    for anime_page_data in recommendations:
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
                            objects.append(recommendation)
                    db.session.bulk_save_objects(objects)
                    db.session.commit()
            return render_template('prediction/get_prediction.html', genres=genres, types=types, sources=sources,
                                   recommendations=recommendations)
        return render_template('prediction/get_prediction.html', genres=genres, types=types, sources=sources)
