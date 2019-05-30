import requests
from subprocess import Popen
from flask import current_app as app

class DownloadSession:
    def __init__(self):
        self.username = app.config['EARTHDATA_USER']
        self.password = app.config['EARTHDATA_PASS']
    
    def download_granule(self, url):
        resp = requests.get(url, stream=True, auth=(self.username, self.password))
        print(resp.status_code)
        if resp.status_code != 200:
            print("not downloaded. Verify that your username and password are correct")
        else:
            resp.raw.decode_content = True
            content = resp.raw
            with open(f'{app.root_path}/data/temp.hdf', 'wb') as outfile:
                while True:
                    chunk = content.read(16 * 1024)
                    if not chunk:
                        break
                    outfile.write(chunk)
