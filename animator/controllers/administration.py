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
from animator.models.models import Profile, Siteuser

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
    print('in user genre')
    have_lists = Profile.query.all()
    users = [Siteuser.query.filter_by(id=profile_id).first() for profile_id in [p.profile_id for p in have_lists]]
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
        plot = series.plot.pie(label='')
        figure = plot.get_figure()
        image = fig_to_base64(figure).decode('utf-8')
        return render_template('administration/administration-user-genre.html', usernames=usernames, image=image)


@bp.route('/administration/user-type', methods=('GET', 'POST'))
@login_required
def administration_panel_user_type():
    print('in user type')
    have_lists = Profile.query.all()
    users = [Siteuser.query.filter_by(id=profile_id).first() for profile_id in [p.profile_id for p in have_lists]]
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
        plot = series.plot.pie(label='')
        figure = plot.get_figure()
        image = fig_to_base64(figure).decode('utf-8')
        return render_template('administration/administration-user-type.html', usernames=usernames, image=image)

