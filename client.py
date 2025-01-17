import base64

import aiohttp
import requests

class OAuthClient:
    http_success_codes = [200, 201, 202, 203, 204, 205, 206, 207, 208, 210, 226]

    def __init__(self, oauth_endpoint, client_id, client_secret):
        self.oauth_endpoint = oauth_endpoint
        self.auth_token = base64.b64encode((client_id + ':' + client_secret).encode('utf-8')).decode('utf-8')

        self.access_token = None
        self.login()

        self.async_session = None
        self.session = requests.Session()

    async def enable_async(self):
        self.async_session = aiohttp.ClientSession()

    async def disable_async(self):
        await self.async_session.close()
        self.async_session = None

    def login(self):
        url = f'{self.oauth_endpoint}'
        request = requests.post(
            url,
            data={'grant_type': 'client_credentials', 'scope': 'all'},
            headers={'Authorization': f'Basic {self.auth_token}'}
        )

        if request.status_code != 200:
            print(f'[ERROR] Request to {url} failed')
            print(f'[ERROR] Error code: {request.status_code}')
            print(f'[ERROR] Content: {request.content}')
            exit(1)
        self.access_token = request.json()['access_token']


    def get(self, url, headers=None):
        if headers is None:
            headers = {}

        if not 'Authorization' in headers:
            headers['Authorization'] = f'Bearer {self.access_token}'

        request = self.session.get(url, headers=headers)
        if request.status_code not in self.http_success_codes:
            print(f'[ERROR] Request to {url} failed')
            print(f'[ERROR] Error code: {request.status_code}')
            print(f'[ERROR] Content: {request.content}')
            exit(1)

        return request


    def post(self, url, data=None, headers=None):
        if headers is None:
            headers = {}

        if not 'Authorization' in headers:
            headers['Authorization'] = f'Bearer {self.access_token}'

        request = self.session.post(url, headers=headers, data=data)
        if request.status_code not in self.http_success_codes:
            print(f'[ERROR] Request to {url} failed')
            print(f'[ERROR] Error code: {request.status_code}')
            print(f'[ERROR] Content: {request.content}')
            exit(1)

        return request

    async def aget(self, url, headers=None):
        if headers is None:
            headers = {}

        if not 'Authorization' in headers:
            headers['Authorization'] = f'Bearer {self.access_token}'

        request = await self.async_session.get(url, headers=headers)
        if request.status not in self.http_success_codes:
            print(f'[ERROR] Request to {url} failed')
            print(f'[ERROR] Error code: {request.status_code}')
            print(f'[ERROR] Content: {request.content}')
            exit(1)

        return request

    async def apost(self, url, data=None, headers=None):
        if headers is None:
            headers = {}

        if not 'Authorization' in headers:
            headers['Authorization'] = f'Bearer {self.access_token}'

        request = await self.async_session.post(url, headers=headers, data=data)
        if request.status not in self.http_success_codes:
            print(f'[ERROR] Request to {url} failed')
            print(f'[ERROR] Error code: {request.status_code}')
            print(f'[ERROR] Content: {request.content}')
            exit(1)

        return request