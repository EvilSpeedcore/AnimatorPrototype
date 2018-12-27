import json
import collections
import io

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import jikanpy.exceptions
import pandas as pd
from pandas import errors

from animator import db, parser
from animator.controllers.auth import login_required
from animator.models.models import Profile


bp = Blueprint('anilist', __name__)


def get_anime_list(mal_username):
    try:
        user = parser.MALUser(mal_username)
    except jikanpy.exceptions.APIException:
        flash('Invalid username.')
    else:
        set_constructor = parser.DataSetConstructor(user.anime_list)
        data = json.dumps(set_constructor.create_data_set())
        return data


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
            data = get_anime_list(mal_username)
            profile = Profile.query.filter_by(profile_id=g.user.id).first()
            if profile:
                profile.list = data
                db.session.commit()
            else:
                profile = Profile(mal_username=mal_username, profile_id=g.user.id, list=data)
                db.session.add(profile)
                db.session.commit()
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
            try:
                data = pd.read_csv(stream)
                d = collections.defaultdict(list)
                for name, values in data.items():
                    d[name] = list(values)
                data = json.dumps(d)
            except errors.ParserError:
                flash('Invalid file format.')
            else:
                profile = Profile.query.filter_by(profile_id=g.user.id).first()
                if profile:
                    profile.list = data
                    db.session.commit()
                else:
                    profile = Profile(mal_username='None', profile_id=g.user.id, list=data)
                    db.session.add(profile)
                    db.session.commit()
                return redirect(url_for('prediction.index'))
        return redirect(url_for('anilist.create'))


@bp.route('/new_title', methods=['GET', 'POST'])
@login_required
def open_new_entry_from():
    return render_template('list_creation/add_title.html')


@bp.route('/add_title', methods=['GET', 'POST'])
@login_required
def add_title():
    if request.method == 'POST':
        profile = Profile.query.filter_by(profile_id=g.user.id).first()
        anime_list = json.loads(profile.list)
        new_title = dict(request.form.items())
        filled_fields = all(bool(item.strip()) for item in new_title.values())
        if not filled_fields:
            flash('Empty fields are not allowed.')
            return render_template('list_creation/add_title.html')
        else:
            for key, value in request.form.items():
                anime_list[key].append(value)
            profile.list = json.dumps(anime_list)
            db.session.commit()
            return redirect(url_for('prediction.index'))
