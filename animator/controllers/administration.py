import base64
import json
import io
from collections import Counter

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import pandas as pd

from animator.controllers.auth import login_required
from animator.models.models import Profile

bp = Blueprint('administration', __name__)


def fig_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png',
                bbox_inches='tight')
    img.seek(0)
    return base64.b64encode(img.getvalue())


@bp.route('/administration', methods=('GET', 'POST'))
@login_required
def administration_panel_index():
    if request.method == 'GET':
        return render_template('administration/administration-index.html')


@bp.route('/administration/user-genre', methods=('GET', 'POST'))
@login_required
def administration_panel_user_genre():
    if request.method == 'GET':
        profile = Profile.query.filter_by(profile_id=g.user.id).first()
        anime_list = json.loads(profile.list)
        counter = Counter(anime_list['Type'])
        series = pd.Series(list(counter.values()), list(counter.keys()))
        plot = series.plot.pie(label='')
        figure = plot.get_figure()
        image = fig_to_base64(figure).decode('utf-8')
        return render_template('administration/administration-user-genre.html', image=image)
