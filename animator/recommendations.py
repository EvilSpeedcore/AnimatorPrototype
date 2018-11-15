from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from animator.auth import login_required
from animator.db import get_db


bp = Blueprint('recommendations', __name__)


@bp.route('/recommendations', methods=('GET', 'POST'))
@login_required
def show_recommendations():

    recommendations = get_db().execute(
        """
        SELECT r.title, r.anime_type, r.episodes, r.studio, r.src, r.genre, r.score
        FROM recommendations r
        WHERE r.profile_id = ?
        """,
        (str(session.get('user_id')))
    ).fetchall()
    return render_template('recommendations/recommendations.html', recommendations=recommendations)
