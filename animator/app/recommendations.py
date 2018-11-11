from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from app.auth import login_required

bp = Blueprint('recommendations', __name__)


@bp.route('/recommendations', methods=('GET', 'POST'))
@login_required
def show_recommendations():
    return render_template('recommendations/recommendations.html')
