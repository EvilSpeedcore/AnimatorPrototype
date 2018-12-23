from flask import (
    Blueprint, render_template, request, session
)
from sqlalchemy import inspect

from animator import db
from animator.controllers.auth import login_required
from animator.models import Recommendations


bp = Blueprint('recommendations', __name__)


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs if c.key not in ('id', 'profile_id')}


def get_user_recommendations():
    recommendations = Recommendations.query.filter_by(profile_id=session.get('user_id')).all()
    recommendations = [object_as_dict(r) for r in recommendations]
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
    recommendation = Recommendations.query.filter_by(title=request.args.get('row_id')).first()
    print(recommendation)
    db.session.delete(recommendation)
    db.session.commit()
    recommendations = get_user_recommendations()
    return render_template('recommendations/recommendations.html', recommendations=recommendations)
