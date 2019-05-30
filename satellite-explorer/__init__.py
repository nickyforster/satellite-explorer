from subprocess import PIPE, Popen
from . import download_images
from flask import Flask, render_template, request, current_app


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')
    app.config.from_pyfile('config.py')

    @app.route('/')
    def landing():
        return render_template('landing_page.html')
    
    @app.route('/data', methods=(['POST']))
    def data():
        if request.method == 'POST':
            data_endpoint = request.form['url']
            # print(data_endpoint)
            # temp_file_loc = f'{current_app.root_path}/data/temp.nc4'
            # curl_p = Popen(['wget', '-O', temp_file_loc, data_endpoint])
            downloading = download_images.DownloadSession()
            downloading.download_granule(data_endpoint)
            # out = curl_p.wait()

            # gdal_t_p_1 = Popen(['gdal_translate', '-of', 'GTiff', f'NETCDF:{temp_file_loc}:sur_refl_b01_1', f'{current_app.root_path}/data/band_1.tif'])
            # out1 = gdal_t_p_1.wait()
            # gdal_t_p_2 = Popen(['gdal_translate', '-of', 'GTiff', f'NETCDF:{temp_file_loc}:sur_refl_b04_1', f'{current_app.root_path}/data/band_4.tif'])
            # out2 = gdal_t_p_2.wait()
            # gdal_t_p_3 = Popen(['gdal_translate', '-of', 'GTiff', f'NETCDF:{temp_file_loc}:sur_refl_b03_1', f'{current_app.root_path}/data/band_3.tif'])
            # out3 = gdal_t_p_3.wait()

            # gdal_merge = Popen(['gdal_merge.py', '-co', 'PHOTOMETRIC=RGB', '-seperate',
            #     current_app.root_path + '/data/band_1.tif',
            #     current_app.root_path + '/data/band_4.tif',
            #     current_app.root_path + '/data/band_3.tif',
            #     '-o', f'{current_app.root_path}/data/final_rgb.tif'])
            # out4 = gdal_merge.wait()
            
            # gdal_warp = Popen(['gdalwarp', '-co', 'PHOTOMETRIC=RGB',
            #     # '-t_srs', '+proj=utm +zone=10 +datum=WGS84',
            #     f'{current_app.root_path}/data/final_rgb.tif',
            #     f'{current_app.root_path}/data/final_rgb_warped.tif'])
            # out5 = gdal_warp.wait()

            return '', 204
        else:
            return 'needs to be a post method', 204
    
    from . import search, results
    app.register_blueprint(search.bp)
    app.register_blueprint(results.bp)

    return app