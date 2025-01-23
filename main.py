import asyncio
import cmd
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from api.client import OAuthClient, CyberArkPlatformClient
from services.manager import ServiceManager

class Cli(cmd.Cmd):
    def __init__(self):
        super().__init__()
        self.prompt = '[] # '
        self.intro = 'Welcome to CyberArk Explorer!'

    service_manager = None
    roles = []

    def preloop(self):
        logging.debug('Allocate new Service Manager')

    def postloop(self):
        logging.debug('Deallocate Service Manager')

    def do_login(self, args):
        """Login to CyberArk Platform"""
        arg_list = args.split(' ')
        if arg_list[0] == '':
            print('Missing argument: file, interactive\n')

        if arg_list[0] == 'file':
            file_path = ''.join(arg_list[1:])
            if file_path != '' and Path(file_path).is_file():
                self.__login_from_env(file_path)
            else:
                self.__login_from_env('.env')
            return

        if arg_list[0] == 'interactive':
            self.__login_from_prompt()
            return

    def do_ls(self, args):
        """List roles and associated services"""
        if len(args) < 1:
            print('Missing argument: roles, services\n')
            return
        elif args == 'roles':
            self.__list_roles()
        elif args == 'services':
            self.__list_services()
        return


    def do_grep(self, args):
        """Grep the selected role based on the search pattern"""
        # if self.service_manager is None:
        #     print('Not logged in')
        #     return

        arg_list = args.split(' ')
        if arg_list[0] == '':
            print('Missing argument: role, data')
            return

        search_pattern = ''.join(arg_list[1:])
        if search_pattern == '':
            print('Missing argument: <name or pattern>')
            return

        if arg_list[0] == 'data':
            self.__grep_data(search_pattern)

        if arg_list[0] == 'role':
            self.__grep_role(search_pattern)

    def do_cat(self, args):
        """Show role and associated services"""
        if not args:
            print('Missing argument: <role name>')
            return

        """Show role content"""
        found = False
        for role in self.roles:
            if role.name == args:
                found = True
                self.__print_role(role)

        if not found:
            print(f'Role {args} not found')

    def do_scan(self, args):
        """Scan for role usage in services. Print results as a tree"""
        if self.service_manager is None:
            print('Not logged in')
            return

        print('Please wait...')
        self.roles = asyncio.run(self.service_manager.run())
        print('Scan complete!')

    def do_enable(self, args):
        """Enable a service to be scanned for role usage"""
        if self.service_manager is None:
            print('Not logged in')
            return

        if not args:
            print('Missing argument: <service name>')
            return

        if self.service_manager.enable(args):
            print(f'Service {args} enabled')
        else:
            print(f'Failed to enable {args}')

    def do_exit(self, args):
        """Exit the program"""
        exit()

    def __list_services(self):
        """List available CyberArk services"""
        print('Services status')
        print('--------------------------------------------------')
        column_size = 40
        for service_name in self.service_manager.services:
            service_status = 'Enabled' if self.service_manager.services[service_name].enabled else 'Disabled'
            service_name_size = len(service_name)
            while service_name_size < column_size:
                service_name += ' '
                service_name_size = service_name_size + 1

            print(f'{service_name} {service_status}')

    def __list_roles(self):
        if len(self.roles) == 0:
            print('No roles found. Please run the \'scan\' command first.')

        for role in self.roles:
            self.__print_role(role)

    def __print_role(self, role):
        print(f'{role}')
        for svc_data in role.services_data:
            if len(svc_data.data) == 0:
                continue

            print(f'  |-> {svc_data.name}')
            for elm in svc_data.data:
                print(f'  |    |-> {elm}')

    def __grep_data(self, search_pattern):
        roles_to_print = []
        for role in self.roles:
            is_done = False
            for service_data in role.services_data:
                if is_done:
                    break
                for elm in service_data.data:
                    if is_done:
                        break
                    if search_pattern in elm.name:
                        is_done = True
                        roles_to_print.append(role)

        for role in roles_to_print:
            self.__print_role(role)

        if len(roles_to_print) == 0:
            print('No roles found')

    def __grep_role(self, search_pattern):
        for role in self.roles:
            if not search_pattern in role.name:
                continue
            self.__print_role(role)

    def __login(self, tenant_id, client_id, client_secret):
        client = CyberArkPlatformClient(tenant_id, client_id, client_secret)
        self.service_manager = ServiceManager(client)
        self.prompt = f'[{tenant_id}] # '
        print(f'Successfully logged in to {tenant_id}')

    def __login_from_env(self, env_path_str):
        env_path = Path(env_path_str)
        if not env_path.exists() or not env_path.is_file():
            print('Missing credentials or environment file')
            return

        print(f'Loading credentials from {env_path_str}')
        load_dotenv(env_path_str)  # SEE https://github.com/Nuitka/Nuitka/issues/2761#issuecomment-2002073468
        tenant_id = os.getenv('TENANT_ID')
        client_id = os.getenv('CLIENT_ID')
        client_secret = os.getenv('CLIENT_SECRET')
        self.__login(tenant_id, client_id, client_secret)

    def __login_from_prompt(self):
        tenant_id = input('Please enter tenant id <eg: acme (for acme.cyberark.cloud)>: ')
        client_id = input('Client id: ')
        client_secret = input('Client secret: ')
        self.__login(tenant_id, client_id, client_secret)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    Cli().cmdloop()