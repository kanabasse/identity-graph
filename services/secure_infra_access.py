import asyncio
import logging

from objects.identity import SIAPolicy, SIAPolicyRule, SIAPolicyRuleMember
from services.service import Service, ServiceData


class SIAPoliciesService(Service):
    def __init__(self, client):
        super().__init__('SIA Policies', client)

    def run(self, roles):
        if not self.enabled:
            logging.warning("Secure Infrastructure Access Service is disabled")
            return roles

        policies = self.get_policies()
        asyncio.run(self.__load_policies_members(policies))

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
                data.append(f'{policy.name} (rule: {rule.name})')

            role.services_data.append(ServiceData('SIA Policies', data))

    def get_policies(self):
        headers = {'Content-Type': 'application/json'}
        get_policies_req = self.client.get(
            f'https://{self.client.subdomain}-jit.cyberark.cloud/api/access-policies',
            headers=headers
        )

        query = get_policies_req.json()
        policies_data = query['items']
        policies = []
        for policy_data in policies_data:
            policy = SIAPolicy(policy_data)
            policies.append(policy)

        return policies

    async def __load_policies_members(self, policies):
        await self.client.enable_async()
        await asyncio.gather(
            *[self.__load_policy_members(policy) for policy in policies],
            return_exceptions = True
        )
        await self.client.disable_async()

    async def __load_policy_members(self, policy):
        headers = {'Content-Type': 'application/json'}
        load_policy_members_req = await self.client.aget(
            f'https://{self.client.subdomain}-jit.cyberark.cloud/api/access-policies/{policy.id}',
            headers=headers
        )

        policy_members_data = await load_policy_members_req.json()
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