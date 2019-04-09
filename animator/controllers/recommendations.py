import json
import random

from flask import (
    Blueprint, render_template, request, session, redirect, url_for, g
)
from sqlalchemy import inspect


from animator import db
from animator.controllers.auth import login_required
from animator.models.models import Profile, Recommendations, TopAnime, Statistics, Siteuser


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
    stats = Statistics.query.filter_by(profile_id=g.user.id).first()
    if stats:
        stats.denied_anime_number += 1
    else:
        stats = Statistics(accepted_anime_number=0, denied_anime_number=1, profile_id=g.user.id)
        db.session.add(stats)
    recommendation = Recommendations.query.filter_by(title=request.args.get('row_id')).first()
    db.session.delete(recommendation)
    db.session.commit()
    return redirect(url_for('recommendations.show_recommendations'))


@bp.route('/add_to_list', methods=('GET', 'POST'))
@login_required
def add_to_list():
    stats = Statistics.query.filter_by(profile_id=g.user.id).first()
    if stats:
        stats.accepted_anime_number += 1
    else:
        stats = Statistics(accepted_anime_number=1, denied_anime_number=0, profile_id=g.user.id)
        db.session.add(stats)
    recommendation = Recommendations.query.filter_by(title=request.args.get('row_id')).first()
    profile = Profile.query.filter_by(profile_id=g.user.id).first()
    anime_list = json.loads(profile.list)
    entry = {'Title': recommendation.title,
             'Type': recommendation.anime_type,
             'Episodes': int(recommendation.episodes),
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


@bp.route('/popular', methods=('GET', 'POST'))
@login_required
def recommendation_by_age():
    if request.method == 'GET':
        users_and_profiles = db.session.query(Siteuser, Profile). \
                filter(Siteuser.id == Profile.profile_id). \
                filter(Siteuser.privilege == 0). \
                filter(Siteuser.age == g.user.age). \
                filter(Siteuser.username != g.user.username). \
                all()
        if not users_and_profiles:
            return render_template('recommendations/recommendation_by_age.html')
        else:
            user, profile = random.choice(users_and_profiles)
            anime_list = json.loads(profile.list)
            favourites = [value for value in zip(*anime_list.values()) if value[-1] >= 8]
            recommendations = random.sample(favourites, 5) if len(favourites) >= 5 else favourites
            fields = ('Title', 'Type', 'Episodes', 'Studio', 'Source', 'Genre', 'Score')
            recommendations = [dict(zip(fields, r)) for r in recommendations]
        return render_template('recommendations/recommendation_by_age.html', recommendations=recommendations)
