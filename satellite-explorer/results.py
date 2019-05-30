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

@bp.route('/', methods=('GET','POST'))
def granule_results():
    if request.method == 'POST':
        lat = request.form['latitude']
        lon = request.form['longitude']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        collection = request.form['collection']

        cmr_session = search_satellites.Session()
        cmr_session.get_token(current_app.config['EARTHDATA_USER'], current_app.config['EARTHDATA_PASS'])
        results = cmr_session.search_granules(start_date, end_date, instrument='MODIS', concept_id=collection, point=f'{lon},{lat}')
        print(results)
        cmr_session.delete_token()

    return render_template('results.html', result=results)