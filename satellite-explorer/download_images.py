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
            total_length = int(resp.headers.get('content-length'))
            dl = 0
            with open(f'{app.root_path}/data/temp.hdf', 'wb') as outfile:
                for data in resp.iter_content(chunk_size=16384):
                    dl += len(data)
                    outfile.write(data)
                    done = int(dl / total_length * 100)
                    print(f'{done}%', end='\r')
