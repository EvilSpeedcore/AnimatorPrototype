import json

from flask import (
    Blueprint, render_template, request, session, redirect, url_for, g
)
from sqlalchemy import inspect


from animator import db
from animator.controllers.auth import login_required
from animator.models.models import Profile, Recommendations, TopAnime


bp = Blueprint('recommendations', __name__)


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs if c.key not in ('id', 'profile_id')}


def get_user_recommendations():
    recommendations = Recommendations.query.filter_by(profile_id=session.get('user_id')).all()
    recommendations = [object_as_dict(r) for r in recommendations]
    return recommendations


def costil():
    import csv
    hehe = []
    with open('top1.csv', newline='', encoding='UTF-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            a = TopAnime(title=row['title'],
                         anime_type=row['type'],
                         episodes=row['episodes'],
                         studio=row['studio'],
                         src=row['src'],
                         genre=row['genre'],
                         score=row['score'],
                         synopsis=row['synopsis'],
                         url=row['url'],
                         image_url=row['image_url'])
            hehe.append(a)
    db.session.add_all(hehe)
    db.session.commit()


@bp.route('/recommendations', methods=('GET', 'POST'))
@login_required
def show_recommendations():
    #  TODO: Add URL to title.
    recommendations = get_user_recommendations()
    return render_template('recommendations/recommendations.html', recommendations=recommendations)


@bp.route('/delete', methods=('GET', 'POST'))
@login_required
def delete_recommendation():
    recommendation = Recommendations.query.filter_by(title=request.args.get('row_id')).first()
    db.session.delete(recommendation)
    db.session.commit()
    return redirect(url_for('recommendations.show_recommendations'))


@bp.route('/add_to_list', methods=('GET', 'POST'))
@login_required
def add_to_list():
    recommendation = Recommendations.query.filter_by(title=request.args.get('row_id')).first()
    profile = Profile.query.filter_by(profile_id=g.user.id).first()
    anime_list = json.loads(profile.list)
    entry = {'Title': recommendation.title,
             'Type': recommendation.anime_type,
             'Episodes': recommendation.episodes,
             'Studios': recommendation.studio,
             'Source': recommendation.src,
             'Genres': recommendation.genre,
             'Score': float(recommendation.score),
             'Personal score': int(request.form.get('personal-score'))}
    for key, value in entry.items():
        anime_list[key].append(value)
    profile.list = json.dumps(anime_list)
    db.session.delete(recommendation)
    db.session.commit()
    return redirect(url_for('recommendations.show_recommendations'))
