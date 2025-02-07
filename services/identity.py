import asyncio
import json
import logging

import aiohttp
from tqdm.asyncio import tqdm_asyncio

from objects.identity import Role, RoleMember, Webapp
from services.service import Service, ServiceData


class IdentityRoleService(Service):
    def __init__(self, client):
        super().__init__('Identity Roles', client)

    async def run(self, roles):
        if not self.enabled:
            logging.warning("Identity Role Service is disabled")
            return roles

        async with aiohttp.ClientSession() as session:
            headers = {'Content-Type': 'application/json'}
            data = {"Script": 'Select ID, COALESCE(Name, ID) AS Name, OrgPath from Role ORDER BY Name COLLATE NOCASE'}
            request = await self.client.apost(
                session,
                f'{self.client.identity_url}/Redrock/Query',
                data=json.dumps(data),
                headers=headers
            )
            roles_data = await request.json()
            for elm in roles_data['Result']['Results']:
                role = Role(elm)
                roles.append(role)

            return roles


class IdentityMembersService(Service):
    def __init__(self, client):
        super().__init__('Identity Members', client)

    async def run(self, roles):
        if not self.enabled:
            logging.warning("Identity Members Service is disabled")
            return roles

        await asyncio.gather(self.__load_roles_members(roles))

    async def __load_roles_members(self, roles):
        async with aiohttp.ClientSession() as session:
            await tqdm_asyncio.gather(
                *[self.__load_role_members(role, session) for role in roles],
                desc="Loading Identity roles members",
                unit='role',
                colour='#ffffff'
            )

    async def __load_role_members(self, role, session):
        headers = {'Content-Type': 'application/json'}
        request = await self.client.apost(
            session,
            f'{self.client.identity_url}/Roles/GetRoleMembers?name='+ role.id,
            headers=headers,
        )
        logging.debug(f'Requesting role members {role.name} --> GET {request.url}')
        role_members_data = await request.json()

        role_members = []
        for elm in role_members_data['Result']['Results']:
            role_members.append(RoleMember(elm['Row']))
        role.services_data.append(ServiceData('Members', role_members))


class IdentityWebAppsService(Service):
    def __init__(self, client):
        super().__init__('Identity WebApps', client)

    async def run(self, roles):
        if not self.enabled:
            logging.warning("Identity WebApp Service is disabled")
            return roles
        return await asyncio.create_task(self.__load_roles_webapps(roles))

    async def __load_roles_webapps(self, roles):
        async with aiohttp.ClientSession() as session:
            roles = await tqdm_asyncio.gather(
                *[self.__load_role_webapps(role, session) for role in roles],
                desc="Loading Identity roles webapps",
                unit='role',
                colour='#ffffff'
            )

            return roles

    async def __load_role_webapps(self, role, session):
        headers = {'Content-Type': 'application/json'}
        request = await self.client.apost(
            session,
            f'{self.client.identity_url}/SaasManage/GetRoleApps?role='+ role.id,
            headers=headers,
        )

        logging.debug(f'Requesting Identity Webapp members {role.id} --> GET {request.url}')

        role_webapps = []
        query = await request.json()
        for elm in query['Result']['Results']:
            role_webapps.append(Webapp(elm['Row']))
        role.services_data.append(ServiceData('Web Apps', role_webapps))

        return role