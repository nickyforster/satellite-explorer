from subprocess import PIPE, Popen
import glob
import os
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
            tif_files = glob.glob(f'{current_app.root_path}/data/*.tif')
            hdf_files = glob.glob(f'{current_app.root_path}/data/*.hdf')
            for file in tif_files:# + hdf_files:
                os.remove(file)

            data_endpoint = request.form['url']
            temp_file_loc = f'{current_app.root_path}/data/temp.hdf'
            downloading = download_images.DownloadSession()
            downloading.download_granule(data_endpoint)

            gdal_warp_1 = Popen(['gdalwarp', '-of', 'GTiff', '-t_srs', 'EPSG:3452',
                f'HDF4_EOS:EOS_GRID:{temp_file_loc}:MODIS_Grid_500m_2D:sur_refl_b01_1', f'{current_app.root_path}/data/temp_band_1.tif'])
            out1 = gdal_warp_1.wait()
            gdal_warp_2 = Popen(['gdalwarp', '-of', 'GTiff', '-t_srs', 'EPSG:3452',
                f'HDF4_EOS:EOS_GRID:{temp_file_loc}:MODIS_Grid_500m_2D:sur_refl_b04_1', f'{current_app.root_path}/data/temp_band_4.tif'])
            out2 = gdal_warp_2.wait()
            gdal_warp_3 = Popen(['gdalwarp', '-of', 'GTiff', '-t_srs', 'EPSG:3452',
                f'HDF4_EOS:EOS_GRID:{temp_file_loc}:MODIS_Grid_500m_2D:sur_refl_b03_1', f'{current_app.root_path}/data/temp_band_3.tif'])
            out3 = gdal_warp_3.wait()

            gdal_merge = Popen(['gdal_merge.py', '-co', 'PHOTOMETRIC=RGB', '-seperate',
                current_app.root_path + '/data/temp_band_1.tif',
                current_app.root_path + '/data/temp_band_4.tif',
                current_app.root_path + '/data/temp_band_3.tif',
                '-o', f'{current_app.root_path}/data/temp_final_rgb.tif'])
            out4 = gdal_merge.wait()

            gdal_scale = Popen(['gdal_translate', f'{current_app.root_path}/data/temp_final_rgb.tif',
                f'{current_app.root_path}/data/temp_final_rgb_scaled.tif', 
                '-scale', '-376', '12897', '0', '65535', '-exponent', '0.5',
                '-co', 'COMPRESS=DEFLATE', '-co', 'COMPRESS=DEFLATE'])
            out5 = gdal_scale.wait()

            contrast_brightness = '25'
            contrast_pivot = '30'
            modulate_brightness = '110'
            modulate_saturation = '60'
            sharpen_radius = '.5'
            sharpen_sigma = '3'
            convert = Popen(['convert', '-channel', 'B', '-gamma', '0.95', '-channel', 'R', '-gamma', '1.01',
                '-channel', 'RGB', '-sigmoidal-contrast', f'{contrast_brightness},{contrast_pivot}%',
                '-modulate', f'{modulate_brightness},{modulate_saturation}', '-sharpen',
                f'{sharpen_radius},{sharpen_sigma}',
                f'{current_app.root_path}/data/temp_final_rgb_scaled.tif',
                f'{current_app.root_path}/data/final_rbg_scaled_cc.tif'])
            out6 = convert.wait()

            return '', 204
        else:
            return 'needs to be a post method', 204
    
    from . import search, results
    app.register_blueprint(search.bp)
    app.register_blueprint(results.bp)

    return app