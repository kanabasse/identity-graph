import asyncio
import json
import logging

from objects.identity import Role, RoleMember
from services.service import Service, ServiceData


class IdentityRoleService(Service):
    def __init__(self, client):
        super().__init__('Identity Roles', client)

    def run(self, roles):
        if not self.enabled:
            logging.warning("Identity Role Service is disabled")
            return roles

        headers = {'Content-Type': 'application/json'}
        data = {"Script": 'Select ID, COALESCE(Name, ID) AS Name, OrgPath from Role ORDER BY Name COLLATE NOCASE'}
        request = self.client.post(
            f'{self.client.identity_url}/Redrock/Query',
            data=json.dumps(data),
            headers=headers
        )
        roles_data = request.json()
        for elm in roles_data['Result']['Results']:
            role = Role(elm)
            roles.append(role)

        return roles


class IdentityMembersService(Service):
    def __init__(self, client):
        super().__init__('Identity Members', client)

    def run(self, roles):
        if not self.enabled:
            logging.warning("Identity Members Service is disabled")
            return roles

        asyncio.run(self.__load_roles_members(roles))

    async def __load_roles_members(self, roles):
        await self.client.enable_async()
        await asyncio.gather(
            *[self.__load_role_members(role) for role in roles],
            return_exceptions = True
        )
        await self.client.disable_async()

    async def __load_role_members(self, role):
        headers = {'Content-Type': 'application/json'}
        request = await self.client.apost(
            f'{self.client.identity_url}/Roles/GetRoleMembers?name='+ role.id,
            headers=headers,
        )
        role_members_data = await request.json()

        role_members = []
        for elm in role_members_data['Result']['Results']:
            role_members.append(RoleMember(elm['Row']))

        role.services_data.append(ServiceData('Members', role_members))


class IdentityWebAppsService(Service):
    def __init__(self, client):
        super().__init__('Identity WebApps', client)

    def run(self, roles):
        if not self.enabled:
            logging.warning("Identity WebApp Service is disabled")
            return roles

        asyncio.run(self.__load_roles_webapps(roles))

    async def __load_roles_webapps(self, roles):
        await self.client.enable_async()
        roles = await asyncio.gather(
            *[self.__load_role_webapps(role) for role in roles],
            return_exceptions = True
        )
        await self.client.disable_async()

        return roles

    async def __load_role_webapps(self, role):
        headers = {'Content-Type': 'application/json'}
        request = await self.client.apost(
            f'{self.client.identity_url}/SaasManage/GetRoleApps?role='+ role.id,
            headers=headers,
        )

        query = await request.json()

        role_webapps = []
        for elm in query['Result']['Results']:
            role_webapps.append(Webapp(elm['Row']))

        role.services_data.append(ServiceData('Web Apps', role_webapps))

        return role