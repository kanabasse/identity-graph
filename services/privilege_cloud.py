import asyncio
import logging

import aiohttp
from tqdm.asyncio import tqdm_asyncio

from objects.identity import Safe, SafeMember
from services.service import Service, ServiceData


class PrivCloudSafeService(Service):
    def __init__(self, client):
        super().__init__('Privilege Cloud Safes', client)

    async def run(self, roles):
        if not self.enabled:
            logging.warning("Privilege Cloud Service is disabled")
            return roles

        safes = await self.get_safes()
        await asyncio.create_task(self.__load_safes_members(safes))

        safes_by_role = {}
        for safe in safes:
            for member in safe.members:
                if member.type == 'Group':
                    if not member.name in safes_by_role:
                        safes_by_role[member.name] = []
                    safes_by_role[member.name].append(safe)

        for role in roles:
            if not role.name in safes_by_role:
                continue
            role.services_data.append(ServiceData('Safes', safes_by_role[role.name]))

    async def get_safes(self):
        async with aiohttp.ClientSession() as session:
            headers = {'Content-Type': 'application/json'}
            get_safes_req = await self.client.aget(
                session,
                f'https://{self.client.subdomain}.privilegecloud.cyberark.cloud/PasswordVault/API/Safes?limit=100000000',
                headers=headers
            )

            query = await get_safes_req.json()
            safes_data = query['value']
            safes = []
            for safe_data in safes_data:
                safe = Safe(safe_data)
                safes.append(safe)

            return safes

    async def __load_safes_members(self, safes):
        async with aiohttp.ClientSession() as session:
            await tqdm_asyncio.gather(
                *[self.__load_safe_members(safe, session) for safe in safes],
                desc="Loading Privilege Cloud safes members",
                unit='safe',
                colour='#ffffff'
            )

    async def __load_safe_members(self, safe, session):
        headers = {'Content-Type': 'application/json'}
        load_safes_members_req = await self.client.aget(
            session,
            f'https://{self.client.subdomain}.privilegecloud.cyberark.cloud/PasswordVault/API/Safes/{safe.id}/Members',
            headers=headers
        )

        logging.debug(f'Requesting safe members {safe.id} --> GET {load_safes_members_req.url}')
        safe_members_data = await load_safes_members_req.json()
        for elm in safe_members_data['value']:
            safe.members.append(SafeMember(elm))