import json
import io
import math

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
import jikanpy.exceptions
import pandas as pd
from pandas import errors

from animator import db, parser
from animator.controllers.auth import login_required
from animator.models.models import Profile, TopAnime
from animator.helpers import object_as_dict
from animator.paginators import TitlePaginator


bp = Blueprint('anilist', __name__)

PAGES_RANGE = 25


def get_top_anime():
    fields = (TopAnime.title, TopAnime.studio, TopAnime.genre, TopAnime.score, TopAnime.url, TopAnime.image_url,
              TopAnime.synopsis)
    titles = [title for title in db.session.query(*fields).all()]
    profile = Profile.query.filter_by(profile_id=g.user.id).first()
    if profile:
        list_ = json.loads(profile.list)
        return [t for t in titles if t[0] not in list_['Title']]
    return titles


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
            try:
                data = pd.read_csv(stream).to_json()
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
        pages = {'current': page_number, 'overall': math.ceil(len(titles) / paginator.PAGE_SIZE)}
        try:
            page = paginator.find(page_number)
        except StopIteration:
            page = paginator.find(1)
            pages = {'current': 1, 'overall': math.ceil(len(titles) / paginator.PAGE_SIZE)}
            return render_template('list_creation/create_from_scratch.html', top=page, pages=pages)
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
    #  Can I use to instead of requirest.args.get?
    #  number = request.form['page']
    number = request.args.get('page')
    titles = get_top_anime()
    paginator = TitlePaginator(titles)
    page = paginator.flip_forward(int(number))
    pages = {'current': page.page_number, 'overall': math.ceil(len(titles) / paginator.PAGE_SIZE)}
    return render_template('list_creation/create_from_scratch.html', top=page, pages=pages)


@bp.route('/add_titles', methods=['POST'])
@login_required
def add_titles():
    title = request.args.get('title')
    score = request.form.get('score')
    titles = get_top_anime()
    paginator = TitlePaginator(titles)
    page = paginator.find(1)
    profile = Profile.query.filter_by(profile_id=g.user.id).first()
    anime = TopAnime.query.filter_by(title=title).first()
    anime = object_as_dict(anime)
    if profile:
        an = {}
        l = (title, anime['anime_type'], int(anime['episodes']), anime['studio'], anime['src'], anime['genre'], float(anime['score']), int(score))
        an['Title'], an['Type'], an['Episodes'], an['Studios'], an['Source'], an['Genres'], an['Score'], an['Personal score'] = l
        anime_list = json.loads(profile.list)
        for key, value in an.items():
            anime_list[key].append(value)
        profile.list = json.dumps(anime_list)
        db.session.commit()
    else:
        list_ = {'Title': [title],
                 'Type': [anime['anime_type']],
                 'Episodes': [int(anime['episodes'])],
                 'Studios': [anime['studio']],
                 'Source': [anime['src']],
                 'Genres': [anime['genre']],
                 'Score': [float(anime['score'])],
                 'Personal score': [int(score)]}
        profile = Profile(mal_username='None', profile_id=g.user.id, list=json.dumps(list_))
        db.session.add(profile)
        db.session.commit()
    return redirect(url_for('anilist.create_from_scratch'))

