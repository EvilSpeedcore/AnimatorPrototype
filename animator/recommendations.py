import asyncio

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from animator.auth import login_required
from animator.db import DBController


bp = Blueprint('recommendations', __name__)
loop = asyncio.get_event_loop()


@bp.route('/recommendations', methods=('GET', 'POST'))
@login_required
def show_recommendations():
    #  TODO: Add URL to title.
    recommendations = DBController.query(
        loop,
        """
        SELECT r.title, r.anime_type, r.episodes, r.studio, r.src, r.genre, r.score, r.synopsis, r.image_url, r.url
        FROM recommendations r
        WHERE r.profile_id = ?
        """,
        (session.get('user_id'), ), is_one=False)
    return render_template('recommendations/recommendations.html', recommendations=recommendations)
