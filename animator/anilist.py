import json
import io
import math

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import jikanpy.exceptions
import pandas as pd

from . import parser
from animator.auth import login_required
from animator.helpers import object_as_dict
from animator.models import Profile, TopAnime
from animator.paginators import TitlePaginator
from animator import db

bp = Blueprint('anilist', __name__)

PAGES_RANGE = 25


def get_top_anime():
    fields = (TopAnime.title, TopAnime.studio, TopAnime.genre, TopAnime.score, TopAnime.url, TopAnime.image_url,
              TopAnime.synopsis)
    titles = [title for title in db.session.query(*fields).all()]
    return titles

@bp.route('/update', methods=('GET', 'POST'))
@login_required
def update():
    return redirect(url_for('anilist.create'))


@bp.route('/create_debug', methods=('GET', 'POST'))
@login_required
def create_debug():
    if request.method == 'POST':
        mal_username = request.form['mal_username']
        if not mal_username:
            flash('MyAnimeList username is required.')
        else:
            try:
                user = parser.MALUser(mal_username)
            except jikanpy.exceptions.APIException:
                flash('Invalid username.')
            else:
                set_constructor = parser.DataSetConstructor(user.anime_list)
                data = json.dumps(set_constructor.create_data_set())
                profile = Profile.query.filter_by(profile_id=g.user.id).first()
                if profile:
                    profile.list = data
                    db.session.commit()
                else:
                    profile = Profile(mal_username=mal_username, profile_id=g.user.id, list=data)
                    db.session.add(profile)
                    db.session.commit()
                return redirect(url_for('prediction.index'))
    return render_template('list_creation/create_list_debug.html')


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        mal_username = request.form['mal_username']
        if not mal_username:
            flash('MyAnimeList username is required.')
        else:
            try:
                user = parser.MALUser(mal_username)
            except jikanpy.exceptions.APIException:
                flash('Invalid username.')
            else:
                set_constructor = parser.DataSetConstructor(user.anime_list)
                data = json.dumps(set_constructor.create_data_set())
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
            data = pd.read_csv(stream).to_json()
            profile = Profile.query.filter_by(profile_id=g.user.id).first()
            if profile:
                profile.list = data
                db.session.commit()
            else:
                profile = Profile(mal_username='None', profile_id=g.user.id, list=data)
                db.session.add(profile)
                db.session.commit()
            return redirect(url_for('prediction.index'))


@bp.route('/create_from_scratch', methods=['GET', 'POST'])
@login_required
def create_from_scratch():
    if request.method == 'GET':
        titles = get_top_anime()
        paginator = TitlePaginator(titles)
        page = paginator.find(1)
        pages = {'current': 1, 'overall': math.ceil(len(titles) / paginator.PAGE_SIZE)}
        return render_template('list_creation/create_from_scratch.html', top=page, pages=pages)
    else:
        page_number = int(request.form['page_number'])
        titles = get_top_anime()
        paginator = TitlePaginator(titles)
        page = paginator.find(page_number)
        pages = {'current': page_number, 'overall': math.ceil(len(titles) / paginator.PAGE_SIZE)}
        return render_template('list_creation/create_from_scratch.html', top=page, pages=pages)


@bp.route('/previous', methods=['GET', 'POST'])
@login_required
def flip_previous():
    number = request.args.get('page')
    titles = get_top_anime()
    paginator = TitlePaginator(titles)
    page = paginator.flip_backwards(int(number))
    pages = {'current': page.page_number, 'overall': math.ceil(len(titles) / paginator.PAGE_SIZE)}
    return render_template('list_creation/create_from_scratch.html', top=page, pages=pages)


@bp.route('/next', methods=['GET', 'POST'])
@login_required
def flip_next():
    number = request.args.get('page')
    titles = get_top_anime()
    paginator = TitlePaginator(titles)
    page = paginator.flip_forward(int(number))
    pages = {'current': page.page_number, 'overall': math.ceil(len(titles) / paginator.PAGE_SIZE)}
    return render_template('list_creation/create_from_scratch.html', top=page, pages=pages)


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

        for key, value in request.form.items():
            anime_list[key].append(value)

        profile.list = json.dumps(anime_list)
        db.session.commit()
    return redirect(url_for('prediction.index'))
