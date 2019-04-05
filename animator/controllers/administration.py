import base64
import json
import io
from collections import Counter

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import pandas as pd

from animator import db
from animator.controllers.auth import login_required
from animator.models.models import Profile, Siteuser, Statistics

bp = Blueprint('administration', __name__)


def fig_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight', dpi=150)
    result = base64.b64encode(img.getvalue())
    fig.clf()
    return result


@bp.route('/administration', methods=('GET', 'POST'))
@login_required
def administration_panel_index():
    if request.method == 'GET':
        return render_template('administration/administration-index.html')


@bp.route('/administration/user-genre', methods=('GET', 'POST'))
@login_required
def administration_panel_user_genre():
    users = [user for user in
             db.session.query(Siteuser).filter(Siteuser.id == Profile.profile_id).all()]
    usernames = [user.username for user in users]
    if request.method == 'GET':
        return render_template('administration/administration-user-genre.html', usernames=usernames)
    elif request.method == 'POST':
        selected_username = request.form['user-selection']
        user = Siteuser.query.filter_by(username=selected_username).first()
        profile = Profile.query.filter_by(profile_id=user.id).first()
        anime_list = json.loads(profile.list)
        counter = Counter(anime_list['Genres'])
        series = pd.Series(list(counter.values()), list(counter.keys()))
        plot = series.plot.pie(label='', labels=None, legend=True)
        figure = plot.get_figure()
        image = fig_to_base64(figure).decode('utf-8')
        return render_template('administration/administration-user-genre.html', usernames=usernames, image=image)


@bp.route('/administration/user-type', methods=('GET', 'POST'))
@login_required
def administration_panel_user_type():
    users = [user for user in
             db.session.query(Siteuser).filter(Siteuser.id == Profile.profile_id).all()]
    usernames = [user.username for user in users]
    if request.method == 'GET':
        return render_template('administration/administration-user-type.html', usernames=usernames)
    elif request.method == 'POST':
        selected_username = request.form['user-selection']
        user = Siteuser.query.filter_by(username=selected_username).first()
        profile = Profile.query.filter_by(profile_id=user.id).first()
        anime_list = json.loads(profile.list)
        counter = Counter(anime_list['Type'])
        series = pd.Series(list(counter.values()), list(counter.keys()))
        plot = series.plot.pie(label='', autopct='%1.0f%%')
        figure = plot.get_figure()
        image = fig_to_base64(figure).decode('utf-8')
        return render_template('administration/administration-user-type.html', usernames=usernames, image=image)


@bp.route('/administration/users-statistics', methods=('GET', 'POST'))
@login_required
def administration_panel_users_statistics():
    stats = [statistic for statistic in
             db.session.query(Statistics).filter(Profile.profile_id == Statistics.profile_id).all()]
    if stats:
        accepted = sum(stat.accepted_anime_number for stat in stats)
        declined = sum(stat.denied_anime_number for stat in stats)
        series = pd.Series([accepted, declined], ['Accepted', 'Declined'])
        plot = series.plot.pie(label='', autopct='%1.0f%%')
        figure = plot.get_figure()
        image = fig_to_base64(figure).decode('utf-8')
    else:
        image = None
    if request.method == 'GET':
        return render_template('administration/administration-users-statistics.html', image=image)


@bp.route('/administration/country-genre', methods=('GET', 'POST'))
@login_required
def administration_panel_country_genre():
    users = [user for user in
             db.session.query(Siteuser).filter(Siteuser.id == Profile.profile_id).all()]
    countries = {user.country for user in users}
    if request.method == 'GET':
        return render_template('administration/administration-country-genre.html', countries=countries)
    elif request.method == 'POST':
        c = Counter()
        selected_country = request.form['country-selection']
        for user, profile in db.session.query(Siteuser, Profile). \
                filter(Siteuser.id == Profile.profile_id). \
                filter(Siteuser.privilege == 0). \
                filter(Siteuser.country == selected_country). \
                all():
            anime_list = json.loads(profile.list)
            counter = Counter(anime_list['Genres'])
            c.update(counter)
        df = pd.DataFrame({'Genres': list(c.keys()), 'Quantity': list(c.values())})
        ax = df.plot.barh(x='Genres', y='Quantity', rot=0, title=selected_country)
        figure = ax.get_figure()
        image = fig_to_base64(figure).decode('utf-8')
        return render_template('administration/administration-country-genre.html', countries=countries, image=image)


@bp.route('/administration/age-genre', methods=('GET', 'POST'))
@login_required
def administration_panel_age_genre():
    users = [user for user in
             db.session.query(Siteuser).filter(Siteuser.id == Profile.profile_id).all()]
    age = {user.age for user in users}
    if request.method == 'GET':
        return render_template('administration/administration-age-genre.html', age=age)
    elif request.method == 'POST':
        c = Counter()
        selected_age = request.form['age-selection']
        for user, profile in db.session.query(Siteuser, Profile). \
                filter(Siteuser.id == Profile.profile_id). \
                filter(Siteuser.privilege == 0). \
                filter(Siteuser.age == selected_age). \
                all():
            anime_list = json.loads(profile.list)
            counter = Counter(anime_list['Genres'])
            c.update(counter)
        df = pd.DataFrame({'Genres': list(c.keys()), 'Quantity': list(c.values())})
        ax = df.plot.barh(x='Genres', y='Quantity', rot=0, title=selected_age)
        figure = ax.get_figure()
        image = fig_to_base64(figure).decode('utf-8')
        return render_template('administration/administration-age-genre.html', age=age, image=image)
