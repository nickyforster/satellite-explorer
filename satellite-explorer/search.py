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

bp = Blueprint('search', __name__, url_prefix='')

@bp.route('/', methods=('GET','POST'))
def search():
    if request.method == 'POST':
        error = None
        lat = request.form['latitude']
        lon = request.form['longitude']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        if not start_date:
            error = 'Start date is required. format=YYYY-MM-DD'
        elif not end_date:
            error = 'End date is required. format=YYYY-MM-DD'
    
        if error is None:
            jamaica_point = '-76.565206,17.863549'
            cmr_session = search_satellites.Session()
            cmr_session.get_token(current_app.config['EARTHDATA_USER'], current_app.config['EARTHDATA_PASS'])
            results = cmr_session.search_collections(start_date, end_date, point=f'{lon},{lat}')
            print(results)
            cmr_session.delete_token()
        return render_template('sat_search.html', result=results)
    else:
        return render_template('search.html')
