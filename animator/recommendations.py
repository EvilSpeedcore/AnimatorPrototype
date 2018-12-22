from flask import (
    Blueprint, render_template, request, session
)

from animator.auth import login_required


bp = Blueprint('recommendations', __name__)


def get_user_recommendations():
    recommendations = DBController.query(
        """
        SELECT r.title, r.anime_type, r.episodes, r.studio, r.src, r.genre, r.score, r.synopsis, r.image_url, r.url
        FROM recommendations r
        WHERE r.profile_id = ?
        """,
        (session.get('user_id'), ), is_one=False)
    return recommendations


@bp.route('/recommendations', methods=('GET', 'POST'))
@login_required
def show_recommendations():
    #  TODO: Add URL to title.
    recommendations = get_user_recommendations()
    return render_template('recommendations/recommendations.html', recommendations=recommendations)


@bp.route('/delete', methods=('GET', 'POST'))
@login_required
def delete_recommendation():
    DBController.update(
                        """
                        DELETE FROM recommendations
                        WHERE title = ?
                        """,
                        (request.args.get('row_id'), ))
    recommendations = get_user_recommendations()
    return render_template('recommendations/recommendations.html', recommendations=recommendations)
