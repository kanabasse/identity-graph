import asyncio
import logging

from objects.identity import Safe, SafeMember
from services.service import Service, ServiceData


class PrivCloudSafeService(Service):
    def __init__(self, client):
        super().__init__('Privilege Cloud Safes', client)

    def run(self, roles):
        if not self.enabled:
            logging.warning("Privilege Cloud Service is disabled")
            return roles

        safes = self.get_safes()
        asyncio.run(self.__load_safes_members(safes))

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

    def get_safes(self):
        headers = {'Content-Type': 'application/json'}
        get_safes_req = self.client.get(
            f'https://{self.client.subdomain}.privilegecloud.cyberark.cloud/PasswordVault/API/Safes?limit=100000000',
            headers=headers
        )

        query = get_safes_req.json()
        safes_data = query['value']
        safes = []
        for safe_data in safes_data:
            safe = Safe(safe_data)
            safes.append(safe)

        return safes

    async def __load_safes_members(self, safes):
        await self.client.enable_async()
        await asyncio.gather(
            *[self.__load_safe_members(safe) for safe in safes],
            return_exceptions = True
        )
        await self.client.disable_async()

    async def __load_safe_members(self, safe):
        headers = {'Content-Type': 'application/json'}
        load_safes_members_req = await self.client.aget(
            f'https://{self.client.subdomain}.privilegecloud.cyberark.cloud/PasswordVault/API/Safes/{safe.id}/Members',
            headers=headers
        )

        safe_members_data = await load_safes_members_req.json()
        for elm in safe_members_data['value']:
            safe.members.append(SafeMember(elm))