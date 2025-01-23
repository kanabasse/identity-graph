import asyncio
import os

from dotenv import load_dotenv

from api.client import CyberArkPlatformClient
from services.identity import IdentityRoleService, IdentityMembersService, IdentityWebAppsService
from services.privilege_cloud import PrivCloudSafeService
from services.secure_cloud_access import SCAPoliciesService
from services.secure_infra_access import SIAPoliciesService

class ServiceManager:
    services = {}
    def __init__(self, client):
        self.services['Roles'] = IdentityRoleService(client)
        self.services['Roles'].enable()

        self.services['Members'] = IdentityMembersService(client)
        self.services['WebApps'] = IdentityWebAppsService(client)
        self.services['PrivilegeCloud'] = PrivCloudSafeService(client)
        self.services['SIA'] = SIAPoliciesService(client)
        self.services['SCA'] = SCAPoliciesService(client)

    def enable(self, name):
        if name == 'all':
            for service in self.services.values():
                service.enable()
            return True

        if name in self.services:
            self.services[name].enable()
            return True
        return False

    def disable(self, name):
        if name in self.services:
            self.services[name].disable()
            return True
        return False

    async def run(self):
        roles = []
        await self.services['Roles'].run(roles)

        # Run all other services afterward
        tasks = []
        for name in self.services:
            if name == 'Roles':
                continue
            if self.services[name].enabled:
                tasks.append(self.services[name].run(roles))
        await asyncio.gather(*tasks)

        return roles