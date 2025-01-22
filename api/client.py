import base64
import logging
from urllib.parse import urlparse

import aiohttp
import requests

class ClientInterface:
    http_success_codes = [200, 201, 202, 203, 204, 205, 206, 207, 208, 210, 226]

    def login(self):
        pass

    def get(self, url, headers=None):
        pass

    def post(self, url, data=None, headers=None):
        pass

    async def enable_async(self):
        pass

    async def disable_async(self):
        pass

    async def aget(self, url, headers=None):
        pass

    async def apost(self, url, data=None, headers=None):
        pass

class OAuthClient(ClientInterface):
    def __init__(self, oauth_endpoint, client_id, client_secret, scope=None):
        self.oauth_endpoint = oauth_endpoint
        self.auth_token = base64.b64encode((client_id + ':' + client_secret).encode('utf-8')).decode('utf-8')
        self.scope = scope

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
        data ={'grant_type': 'client_credentials'}
        if self.scope is not None:
            data['scope'] = self.scope

        request = requests.post(
            url,
            data=data,
            headers={'Authorization': f'Basic {self.auth_token}'}
        )

        if request.status_code != 200:
            logging.error(f'Request to {url} failed')
            logging.error(f'Error code: {request.status_code}')
            logging.error(f'Content: {request.content}')
            exit(1)
        self.access_token = request.json()['access_token']


    def get(self, url, headers=None):
        if headers is None:
            headers = {}

        if not 'Authorization' in headers:
            headers['Authorization'] = f'Bearer {self.access_token}'

        request = self.session.get(url, headers=headers)
        if request.status_code not in self.http_success_codes:
            logging.error(f'Request to {url} failed')
            logging.error(f'Error code: {request.status_code}')
            logging.error(f'Content: {request.content}')
            exit(1)

        return request


    def post(self, url, data=None, headers=None):
        if headers is None:
            headers = {}

        if not 'Authorization' in headers:
            headers['Authorization'] = f'Bearer {self.access_token}'

        request = self.session.post(url, headers=headers, data=data)
        if request.status_code not in self.http_success_codes:
            logging.error(f'Request to {url} failed')
            logging.error(f'Error code: {request.status_code}')
            logging.error(f'Content: {request.content}')
            exit(1)

        return request

    async def aget(self, url, headers=None):
        if headers is None:
            headers = {}

        if not 'Authorization' in headers:
            headers['Authorization'] = f'Bearer {self.access_token}'

        request = await self.async_session.get(url, headers=headers)
        if request.status not in self.http_success_codes:
            logging.error(f'Request to {url} failed')
            logging.error(f'Error code: {request.status_code}')
            logging.error(f'Content: {request.content}')
            exit(1)

        return request

    async def apost(self, url, data=None, headers=None):
        if headers is None:
            headers = {}

        if not 'Authorization' in headers:
            headers['Authorization'] = f'Bearer {self.access_token}'

        request = await self.async_session.post(url, headers=headers, data=data)
        if request.status not in self.http_success_codes:
            logging.error(f'Request to {url} failed')
            logging.error(f'Error code: {request.status_code}')
            logging.error(f'Content: {request.content}')
            exit(1)

        return request

class CyberArkPlatformClient(OAuthClient):
    def __init__(self, subdomain, client_id, client_secret):
        self.subdomain = subdomain
        self.identity_url = self.__get_identity_url()
        super().__init__(f'{self.__get_identity_url()}/oauth2/platformtoken', client_id, client_secret)

    def __get_identity_url(self):
        req = requests.get(f'https://{self.subdomain}.cyberark.cloud/shell/api/endpoint/{self.subdomain}')

        if req.status_code != 200:
            logging.error(f'Fail to get Identity URL for subdomain {self.subdomain}')
            logging.error(f'Error code: {req.status_code}')
            logging.error(f'Content: {req.content}')
            exit(1)

        json = req.json()
        return f'https://{json["fqdn"]}'