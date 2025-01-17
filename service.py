import asyncio
import json

from identity import Role, RoleMember, SafeMember, Safe, Webapp, SIAPolicy, SIAPolicyRuleMember, SIAPolicyRule, \
    SCAPolicy, SCAPolicyMember

class ServiceData:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def __str__(self):
        return self.name


class Service:
    def __init__(self, name, client):
        self.name = name
        self.client = client

    def run(self, roles):
        pass


class IdentityService(Service):
    def __init__(self, name, client, identity_endpoint):
        super().__init__(name, client)
        self.identity_endpoint = identity_endpoint


class PlatformService(Service):
    def __init__(self, name, client, tenant_id):
        super().__init__(name, client)
        self.tenant_id = tenant_id


class IdentityRoleService(IdentityService):
    def __init__(self, client, identity_endpoint):
        super().__init__('Identity Roles', client, identity_endpoint)

    def run(self, roles):
        headers = {'Content-Type': 'application/json'}
        data = {"Script": 'Select ID, COALESCE(Name, ID) AS Name, OrgPath from Role ORDER BY Name COLLATE NOCASE'}
        request = self.client.post(
            f'{self.identity_endpoint}/Redrock/Query',
            data=json.dumps(data),
            headers=headers
        )
        roles_data = request.json()
        for elm in roles_data['Result']['Results']:
            role = Role(elm)
            roles.append(role)

        return roles


class IdentityMembersService(IdentityService):
    def __init__(self, client, identity_endpoint):
        super().__init__('Identity Members', client, identity_endpoint)

    def run(self, roles):
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
            f'{self.identity_endpoint}/Roles/GetRoleMembers?name='+ role.id,
            headers=headers,
        )
        role_members_data = await request.json()

        role_members = []
        for elm in role_members_data['Result']['Results']:
            role_members.append(RoleMember(elm['Row']))

        role.services_data.append(ServiceData('Members', role_members))


class IdentityWebAppsService(IdentityService):
    def __init__(self, client, identity_endpoint):
        super().__init__('Identity WebApps', client, identity_endpoint)

    def run(self, roles):
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
            f'{self.identity_endpoint}/SaasManage/GetRoleApps?role='+ role.id,
            headers=headers,
        )

        query = await request.json()

        role_webapps = []
        for elm in query['Result']['Results']:
            role_webapps.append(Webapp(elm['Row']))

        role.services_data.append(ServiceData('Web Apps', role_webapps))

        return role


class PrivCloudSafeService(PlatformService):
    def __init__(self, client, tenant_id):
        super().__init__('Privilege Cloud Safes', client, tenant_id)

    def run(self, roles):
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
            f'https://{self.tenant_id}.privilegecloud.cyberark.cloud/PasswordVault/API/Safes?limit=100000000',
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
            f'https://{self.tenant_id}.privilegecloud.cyberark.cloud/PasswordVault/API/Safes/{safe.id}/Members',
            headers=headers
        )

        safe_members_data = await load_safes_members_req.json()
        for elm in safe_members_data['value']:
            safe.members.append(SafeMember(elm))


class SCAPoliciesService(PlatformService):
    def __init__(self, client, tenant_id):
        super().__init__('SCA Policies', client, tenant_id)

    def run(self, roles):
        policies = self.get_policies()
        asyncio.run(self.__load_policies_members(policies))

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

    def get_policies(self):
        headers = {'Content-Type': 'application/json'}
        get_policies_req = self.client.get(
            f'https://{self.tenant_id}.sca.cyberark.cloud/api/policies',
            headers=headers
        )

        query = get_policies_req.json()
        policies_data = query['hits']
        policies = []
        for policy_data in policies_data:
            policy = SCAPolicy(policy_data)
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
            f'https://{self.tenant_id}.sca.cyberark.cloud/api/policies/{policy.id}',
            headers=headers
        )

        policy_members_data = await load_policy_members_req.json()
        for elm in policy_members_data['entities']:
            policy.members.append(SCAPolicyMember(elm))

class SIAPoliciesService(PlatformService):
    def __init__(self, client, tenant_id):
        super().__init__('SIA Policies', client, tenant_id)

    def run(self, roles):
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
            f'https://{self.tenant_id}-jit.cyberark.cloud/api/access-policies',
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
            f'https://{self.tenant_id}-jit.cyberark.cloud/api/access-policies/{policy.id}',
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
