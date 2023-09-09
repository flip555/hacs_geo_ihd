import requests
import json
import time
import os
from functools import partial

GEO_BASE_URL = 'https://api.geotogether.com'

TOKEN_FILE = '/tmp/token.json'
SYSTEM_ID_FILE = '/tmp/systemId.json'
PERIODIC_DATA_FILE = '/tmp/periodicData.json'
LIVE_DATA_FILE = '/tmp/liveData.json'
DEVICE_DATA_FILE = '/tmp/deviceData.json'


class GeoHelper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.apiCallsCounter = 0



    async def make_request(self, hass, url, method='GET', params={}, headers={}, json_body=None):
        func = partial(requests.request, method, GEO_BASE_URL + url, params=params, headers=headers, json=json_body)
        response = await hass.async_add_executor_job(func)
        response.raise_for_status()
        return response.json()


    async def login(self, hass):
        headers = {'Content-Type': 'application/json'}
        body = {'identity': self.username, 'password': self.password}
        response = await self.make_request(hass, '/usersservice/v2/login', 'POST', headers=headers, json_body=body)
        return response['accessToken']

    async def get_device_data(self, hass, access_token):
        headers = {'Authorization': f"Bearer {access_token}"}
        return await self.make_request(hass, '/api/userapi/v2/user/detail-systems?systemDetails=true', 'GET', headers=headers)

    async def get_periodic_meter_data(self, hass, access_token, system_id):
        headers = {'Authorization': f"Bearer {access_token}"}
        return await self.make_request(hass, f"/api/userapi/system/smets2-periodic-data/{system_id}", 'GET', headers=headers)

    async def get_live_meter_data(self, hass, access_token, system_id):
        headers = {'Authorization': f"Bearer {access_token}"}
        return await self.make_request(hass, f"/api/userapi/system/smets2-live-data/{system_id}", 'GET', headers=headers)

    def cache_to_file(self, filename, data):
        with open(filename, 'w') as file:
            json.dump({'timestamp': time.time(), 'data': data}, file)

    def get_from_cache(self, filename, expire_time):
        if not os.path.exists(filename):
            return None
        with open(filename, 'r') as file:
            cached_data = json.load(file)
        if time.time() - cached_data['timestamp'] <= expire_time:
            return cached_data['data']
        return None

    async def get_consolidated_data(self, hass):
        try:
            token = self.get_from_cache(TOKEN_FILE, 3600) or await self.login(hass)
            self.cache_to_file(TOKEN_FILE, token)
            system_id = self.get_from_cache(SYSTEM_ID_FILE, 3600) or (await self.get_device_data(hass, token))["systemRoles"][0]["systemId"]
            self.cache_to_file(SYSTEM_ID_FILE, system_id)

            periodic_meter_data = self.get_from_cache(PERIODIC_DATA_FILE, 600) or await self.get_periodic_meter_data(hass, token, system_id)
            self.cache_to_file(PERIODIC_DATA_FILE, periodic_meter_data)

            live_meter_data = self.get_from_cache(LIVE_DATA_FILE, 5) or await self.get_live_meter_data(hass, token, system_id)
            self.cache_to_file(LIVE_DATA_FILE, live_meter_data)

            device_data = self.get_from_cache(DEVICE_DATA_FILE, 3600) or await self.get_device_data(hass, token)
            self.cache_to_file(DEVICE_DATA_FILE, device_data)

            consolidated_data = {
                'PeriodicMeterData': periodic_meter_data,
                'LiveMeterData': live_meter_data,
                'DeviceData': device_data,
                'apiCallsCount': self.apiCallsCounter
            }

            return json.dumps(consolidated_data)

        except Exception as e:
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
            if os.path.exists(SYSTEM_ID_FILE):
                os.remove(SYSTEM_ID_FILE)
            raise e
