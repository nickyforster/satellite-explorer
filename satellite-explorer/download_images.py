import requests
from subprocess import Popen
from flask import current_app as app

class DownloadSession:
    def __init__(self):
        self.username = app.config['EARTHDATA_USER']
        self.password = app.config['EARTHDATA_PASS']
    
    def download_granule(self, url):
    ## https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+Python
        with requests.Session() as session:
            session.auth = (self.username, self.password)
            r1 = session.request('get', url)
            r = session.get(r1.url, auth=(self.username, self.password), stream=True)
            if r.status_code != 200:
                print(r.content)
                print("not downloaded. Verify that your username and password are correct")
            elif r.ok:
                print("Got the data...")
                total_length = int(r.headers.get('content-length'))
                dl = 0
                with open(f'{app.root_path}/data/temp.hdf', 'wb') as outfile:
                    for data in r.iter_content(chunk_size=16384):
                        dl += len(data)
                        outfile.write(data)
                        done = int(dl / total_length * 100)
                        print(f'{done}%', end='\r')
