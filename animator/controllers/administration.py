from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from animator.controllers.auth import login_required

bp = Blueprint('administration', __name__)


@bp.route('/administration', methods=('GET', 'POST'))
@login_required
def administration_panel():
    return render_template('administration/administration-index.html')