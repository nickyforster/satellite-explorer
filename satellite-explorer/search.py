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

bp = Blueprint('search', __name__, url_prefix='/search')

@bp.route('/search-before-after', methods=('GET','POST'))
def search_before_after():
    if request.method == 'POST':
        error=None
        lat = request.form['latitude']
        lon = request.form['longitude']
        start_date = request.form['start_date'] + 'T00:00:00Z'
        start_date_end = request.form['start_date'] + 'T23:59:59Z'
        end_date = request.form['end_date'] + 'T00:00:00Z'
        end_date_end = request.form['end_date'] + 'T23:59:59Z'

        if not start_date:
            error = 'Start date is required. format=YYYY-MM-DD'
        elif not end_date:
            error = 'End date is required. format=YYYY-MM-DD'
    
        if error is None:
            ## start the session
            cmr_session = search_satellites.Session()
            cmr_session.get_token(current_app.config['EARTHDATA_USER'], current_app.config['EARTHDATA_PASS'])

            ## get the collection results
            results_terra_before = cmr_session.search_granules(start_date, start_date_end, point=f'{lon},{lat}',
                instrument='MODIS', short_name='MOD09GA')
            results_terra_after = cmr_session.search_granules(end_date, end_date_end, point=f'{lon},{lat}',
                instrument='MODIS', short_name='MOD09GA')
            results_aqua_before = cmr_session.search_granules(start_date, start_date_end, point=f'{lon},{lat}',
                instrument='MODIS', short_name='MYD09GA')
            results_aqua_after = cmr_session.search_granules(end_date, end_date_end, point=f'{lon},{lat}',
                instrument='MODIS', short_name='MYD09GA')

            ## end the session
            cmr_session.delete_token()
        
        results = {
            'terra_before': results_terra_before,
            'terra_after': results_terra_after,
            'aqua_before': results_aqua_before,
            'aqua_after': results_aqua_after
        }
        return render_template('results.html', result=results)
    else:
        return render_template('before_after.html')
