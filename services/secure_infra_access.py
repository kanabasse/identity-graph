import asyncio
import logging

import aiohttp
from tqdm.asyncio import tqdm_asyncio

from objects.identity import SIAPolicy, SIAPolicyRule, SIAPolicyRuleMember
from services.service import Service, ServiceData


class SIAPoliciesService(Service):
    def __init__(self, client):
        super().__init__('SIA Policies', client)

    async def run(self, roles):
        if not self.enabled:
            logging.warning("Secure Infrastructure Access Service is disabled")
            return roles

        policies = await self.get_policies()
        await asyncio.create_task(self.__load_policies_members(policies))

        policyrules_by_role = {}
        for policy in policies:
            for rule in policy.rules:
                for member in rule.members:
                    if member.type == 'Role':
                        if not member.name in policyrules_by_role:
                            policyrules_by_role[member.name] = []
                        policyrules_by_role[member.name].append((rule, policy))

        for role in roles:
            if not role.name in policyrules_by_role:
                continue
            data = []
            for (rule, policy) in policyrules_by_role[role.name]:
                data.append(rule)

            role.services_data.append(ServiceData('SIA Policies', data))

    async def get_policies(self):
        async with aiohttp.ClientSession() as session:
            headers = {'Content-Type': 'application/json'}
            get_policies_req = await self.client.aget(
                session,
                f'https://{self.client.subdomain}-jit.cyberark.cloud/api/access-policies',
                headers=headers
            )

            query = await get_policies_req.json()
            policies_data = query['items']
            policies = []
            for policy_data in policies_data:
                policy = SIAPolicy(policy_data)
                policies.append(policy)

            return policies

    async def __load_policies_members(self, policies):
        async with aiohttp.ClientSession() as session:
            await tqdm_asyncio.gather(
                *[self.__load_policy_members(policy, session) for policy in policies],
                desc="Loading SIA policy members",
                unit='policy',
                colour='#ffffff'
            )

    async def __load_policy_members(self, policy, session):
        headers = {'Content-Type': 'application/json'}
        request = await self.client.aget(
            session,
            f'https://{self.client.subdomain}-jit.cyberark.cloud/api/access-policies/{policy.id}',
            headers=headers
        )

        logging.debug(f'Requesting SIA policy members {policy.id} --> GET {request.url}')
        policy_members_data = await request.json()
        for rule_data in policy_members_data['userAccessRules']:
            rule = SIAPolicyRule(rule_data, policy.name)

            if not 'userData' in rule_data:
                continue

            if 'roles' in rule_data['userData']:
                for role in rule_data['userData']['roles']:
                    rule.members.append(SIAPolicyRuleMember(role['name'], 'Role'))

            if 'users' in rule_data['userData']:
                for user in rule_data['userData']['users']:
                    rule.members.append(SIAPolicyRuleMember(user['name'], 'User'))

            if 'groups' in rule_data['userData']:
                for group in rule_data['userData']['groups']:
                    rule.members.append(SIAPolicyRuleMember(group['name'], 'Group'))

            policy.rules.append(rule)