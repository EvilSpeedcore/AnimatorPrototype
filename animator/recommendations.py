import asyncio

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from animator.auth import login_required
from animator.db import DBController


bp = Blueprint('recommendations', __name__)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


@bp.route('/recommendations', methods=('GET', 'POST'))
@login_required
def show_recommendations():
    #  TODO: Add URL to title.
    recommendations = DBController.query(
        """
        SELECT r.title, r.anime_type, r.episodes, r.studio, r.src, r.genre, r.score
        FROM recommendations r
        WHERE r.profile_id = ?
        """,
        (session.get('user_id'), ), is_one=False, loop=loop)
    return render_template('recommendations/recommendations.html', recommendations=recommendations)
