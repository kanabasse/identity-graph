import os

from client import OAuthClient
from service import IdentityWebAppsService, IdentityMembersService, PrivCloudSafeService, \
    IdentityRoleService, SIAPoliciesService, SCAPoliciesService

from dotenv import load_dotenv


class IdentityManager:
    services = []

    def __init__(self):
        load_dotenv()
        client_id = os.getenv('CLIENT_ID')
        client_secret = os.getenv('CLIENT_SECRET')

        self.identity_endpoint = os.getenv('IDENTITY_ENDPOINT')
        self.tenant_id = os.getenv('TENANT_ID')

        self.identity_client = OAuthClient(f'{self.identity_endpoint}/oauth2/token/IdentityGraphAuth', client_id, client_secret)
        self.services_client = OAuthClient(f'{self.identity_endpoint}/oauth2/platformtoken', client_id, client_secret)

        self.role_service = IdentityRoleService(self.identity_client, self.identity_endpoint)

    def enable_service(self, name):
        if name == 'Identity':
            self.services.append(IdentityMembersService(self.identity_client, self.identity_endpoint))
            self.services.append(IdentityWebAppsService(self.identity_client, self.identity_endpoint))
            return

        if name == 'Privilege Cloud':
            self.services.append(PrivCloudSafeService(self.services_client, self.tenant_id))
            return

        if name == 'SIA':
            self.services.append(SIAPoliciesService(self.services_client, self.tenant_id))
            return

        if name == 'SCA':
            self.services.append(SCAPoliciesService(self.services_client, self.tenant_id))
            return

    def run(self):
        roles = []
        self.role_service.run(roles)
        for svc in self.services:
            svc.run(roles)

        return roles

identity_manager = IdentityManager()
identity_manager.enable_service('Identity')
identity_manager.enable_service('Privilege Cloud')
identity_manager.enable_service('SIA')
identity_manager.enable_service('SCA')

roles = identity_manager.run()
for role in roles:
    print(f'[INFO] {role}')
    for svc_data in role.services_data:
        if len(svc_data.data) == 0:
            continue

        print(f'[INFO]  |-> {svc_data.name}')
        for elm in svc_data.data:
            print(f'[INFO]  |    |-> {elm}')
