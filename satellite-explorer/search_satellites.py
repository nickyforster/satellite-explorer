import requests
import xmltodict
from flask import current_app as app
import re

pool_domain = re.compile(r'(e4ftl01.cr.usgs.gov)')
hdf_file_end = re.compile(r'(.hdf$)')
class Session:
    """main session class for interacting with the nasa cmr"""
    def __init__(self):
        self.token = None
        self.client_id = app.config['CLIENT_ID']
    
    def get_token(self, username, password):
        token_url = "https://cmr.earthdata.nasa.gov/legacy-services/rest/tokens"
        payload = f"<token><username>{username}</username><password>{password}</password><client_id>{self.client_id}</client_id><user_ip_address>192.168.1.1</user_ip_address> </token>"
        headers = { 'Content-Type': 'application/xml' }
        resp = requests.post(token_url,data=payload,headers=headers).text
        resp_dict = xmltodict.parse(resp)
        self.token = resp_dict['token']['id']

    def delete_token(self):
        token_url = f"https://cmr.earthdata.nasa.gov/legacy-services/rest/tokens/{self.token}"
        headers = { 'Content-Type': 'application/xml' }
        resp = requests.delete(token_url, headers=headers)
        resp_code = resp.status_code
        if resp_code == 204:
            print('token deleted')
        else:
            print('couldn\'t delete token')
    
    ## There are three different environments for the CMR system
    ## Systems Integration Test, User Acceptance Test and Operations/Production
    ## We're using Operations/Production (open to users around the world) – https://cmr.earthdata.nasa.gov/
    ## query params: page_size, page_num, offset, scroll, sort_key, pretty, token, echo_compatible
    ## You can search for collections, granules and tiles
    ## You can find collections a lot of different ways, we'll start with temporal and bounds
    ## The temporal datetime has to be in yyyy-MM-ddTHH:mm:ssZ format, range is inclusive for bounds default

    ## Test case: look for a bay in jamaica before and after a hurricane
    ## Hurricane Dean, August 19 2007
    ## Yallahs bay, 17.863549, -76.565206

    def search_collections(self, start_date, end_date, platform='', instrument='', point='', short_name=''):
        search_collection_url = "https://cmr.earthdata.nasa.gov/search/collections"
        headers = {
            'Echo-Token': self.token,
            'Accept': 'application/json',
            'Client-Id': self.client_id
        }
        payload = {
            'temporal': f'{start_date},{end_date}',
            'point': f'{point}',
            'downloadable': 'true',
            'include_granule_counts': 'true',
            'platform': platform,
            'instrument': instrument,
            'short_name': short_name
        }
        resp = requests.post(search_collection_url, headers=headers, data=payload).json()
        results = resp['feed']['entry'] ## this is a list
        ids = []
        for result in results:
            if int(result['granule_count']) > 0:
                ids.append((result['id'], result['title'], result['summary'], result['granule_count']))
        return ids
    
    def search_granules(self, start_date, end_date, concept_id='', instrument='',
        day_night='unspecified', point='', short_name=''):
        search_granules_url = "https://cmr.earthdata.nasa.gov/search/granules"
        headers = {
            'Echo-Token': self.token,
            'Accept': 'application/json',
            'Client-Id': self.client_id
        }
        payload = {
            # 'concept_id': concept_id,
            'short_name': short_name,
            'temporal': f'{start_date},{end_date}',
            'point': f'{point}',
            'downloadable': 'true',
            'instrument': instrument,
            # 'day_night_flag': day_night,
        }
        resp = requests.post(search_granules_url, headers=headers, data=payload).json()
        results = resp['feed']['entry'] ## this is a list
        jpgs_hdfs = []
        for result in results:
            links = {}
            for link in result['links']:
                if link['href'][-4:] == '.jpg':
                    links['jpg'] = link['href']
                elif pool_domain.search(link['href']) and hdf_file_end.search(link['href']):
                    # built_link = link['href'] + '.nc4?sur_refl_b01_1[0:1:2399][0:1:2399],sur_refl_b04_1[0:1:2399][0:1:2399],sur_refl_b03_1[0:1:2399][0:1:2399]'
                    built_link = link['href']
                    print(built_link)
                    links['hdf'] = built_link
            if len(links.keys()) > 1:
                jpgs_hdfs.append((links['jpg'], links['hdf']))
            else:
                jpgs_hdfs.append([])

        return jpgs_hdfs
    
    def search_granule_timelines(self, start_date, end_date, point='-76.565206,17.863549'):
        pass
