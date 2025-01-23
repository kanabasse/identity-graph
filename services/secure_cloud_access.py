import asyncio
import logging

import aiohttp

from objects.identity import SCAPolicy, SCAPolicyMember
from services.service import Service, ServiceData


class SCAPoliciesService(Service):
    def __init__(self, client):
        super().__init__('SCA Policies', client)

    async def run(self, roles):
        if not self.enabled:
            logging.warning("Secure Cloud Access Service is disabled")
            return roles

        policies = await self.get_policies()
        await asyncio.create_task(self.__load_policies_members(policies))

        policies_by_role = {}
        for policy in policies:
            for member in policy.members:
                if member.type == 'role':
                    if not member.name in policies_by_role:
                        policies_by_role[member.name] = []
                    policies_by_role[member.name].append(policy)

        for role in roles:
            if not role.name in policies_by_role:
                continue
            role.services_data.append(ServiceData('SCA Policies', policies_by_role[role.name]))

    async def get_policies(self):
        async with aiohttp.ClientSession() as session:
            headers = {'Content-Type': 'application/json'}
            get_policies_req = await self.client.aget(
                session,
                f'https://{self.client.subdomain}.sca.cyberark.cloud/api/policies',
                headers=headers
            )

            query = await get_policies_req.json()
            policies_data = query['hits']
            policies = []
            for policy_data in policies_data:
                policy = SCAPolicy(policy_data)
                policies.append(policy)

            return policies

    async def __load_policies_members(self, policies):
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *[self.__load_policy_members(policy, session) for policy in policies],
                return_exceptions = True
            )

    async def __load_policy_members(self, policy, session):
        headers = {'Content-Type': 'application/json'}
        request = await self.client.aget(
            session,
            f'https://{self.client.subdomain}.sca.cyberark.cloud/api/policies/{policy.id}',
            headers=headers
        )

        logging.debug(f'Requesting SCA policy members {policy.id} --> GET {request.url}')
        policy_members_data = await request.json()
        for elm in policy_members_data['entities']:
            policy.members.append(SCAPolicyMember(elm))