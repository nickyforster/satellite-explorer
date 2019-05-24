import functools
from . import search_satellites

from flask import (
    Blueprint,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app
)

bp = Blueprint('results', __name__, url_prefix='/results')
@bp.route('/collections_results', methods=('GET', 'POST'))

def collections_results():
    return render_template('results.html')