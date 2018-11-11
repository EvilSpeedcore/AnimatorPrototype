from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)


bp = Blueprint('recommendations', __name__)


@bp.route('/recommendations', methods=('GET', 'POST'))
def show_recommendations():
    return render_template('recommendations/show.html')
