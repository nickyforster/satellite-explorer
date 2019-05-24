import requests
import xmltodict
from flask import current_app as app

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

    def search_collections(self, start_date, end_date, platform='', instrument='', point=''):
        search_collection_url = "https://cmr.earthdata.nasa.gov/search/collections"
        headers = {
            'Echo-Token': self.token,
            'Accept': 'application/json',
            'Client-Id': self.client_id
        }
        payload = {
            'temporal': f'{start_date}T00:00:00Z,{end_date}T00:00:00Z',
            'point': f'{point}',
            'downloadable': 'true',
            'include_granule_counts': 'true',
            'platform': platform,
            'instrument': instrument
        }
        resp = requests.post(search_collection_url, headers=headers, data=payload).json()
        results = resp['feed']['entry'] ## this is a list
        ## 'processing_level_id', 'boxes', 'time_start', 'dif_ids', 'version_id', 'dataset_id', 'has_spatial_subsetting',
        ## 'has_transforms', 'associations', 'has_variables', 'data_center', 'short_name', 'organizations', 'title',
        ## 'coordinate_system', 'summary', 'orbit_parameters', 'id', 'has_formats', 'original_format', 'collection_data_type',
        ## 'browse_flag', 'online_access_flag', 'links'
        ids = []
        for result in results:
            if int(result['granule_count']) > 0:
                ids.append(result["dataset_id"])
                # print(f'dataset: {result["dataset_id"]}\ntime start: {result["time_start"]}\n\
                    # granules: {result["granule_count"]}\nid:{result["id"]}\n\n')
        return ids
    
    def search_granules(self, start_date, end_date, concept_id='', instrument='',
        day_night='unspecified', point=''):
        search_granules_url = "https://cmr.earthdata.nasa.gov/search/granules"
        headers = {
            'Echo-Token': self.token,
            'Accept': 'application/json',
            'Client-Id': self.client_id
        }
        payload = {
            'concept_id': concept_id,
            'temporal': f'{start_date}T00:00:00Z,{end_date}T00:00:00Z',
            'point': f'{point}',
            'downloadable': 'true',
            'instrument': instrument,
            'day_night_flag': day_night
        }
        resp = requests.post(search_granules_url, headers=headers, data=payload).json()
        results = resp['feed']['entry'] ## this is a list
        for result in results:
            for link in result['links']:
                if link['href'][-4:] == '.jpg' or link['href'][-4:] == '.hdf':
                    print(link['href'])
    
    def search_granule_timelines(self, start_date, end_date, point='-76.565206,17.863549'):
        pass

## MODIS -- aqua and terra
# cmr_session.search_collections('2007-08-16', '2007-08-21', instrument='MODIS')
## landsat
# cmr_session.search_collections('2007-08-19', '2007-08-21', point=jamaica_point)

## Terra platform
# cmr_session.search_granules('2007-08-16', '2007-08-21', concept_id='C203234448-LAADS', instrument='MODIS'
#     point=jamaica_point)

## Aqua platform
# cmr_session.search_granules('2007-08-16', '2007-08-21', concept_id='C203234523-LAADS', instrument='MODIS',
#     point=jamaica_point)
