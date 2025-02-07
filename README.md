# Identity Graph - A CyberArk Identity role scanner 

Identity Graph is a role scanner, it discovers usage of roles in CyberArk services such as SIA, SCA and Privilege Cloud.
Roles are displayed with its associated services as such:

```bash
[tenant-name] # list roles
My Role1
 |-> Members
 |    |-> Another role
 |    |-> some_user@cyberark.cloud.1234
 |-> Web Apps
 |    |-> My WebApp1
 |    |-> My WebApp2
 |    |-> My WebApp3
 |    |-> My WebApp4
 |-> Safes
 |    |-> Windows_Local_Users
 |    |-> Windows_Domain_Users
 |    |-> Linux_SSH_Users
 |-> SIA Policies
 |    |-> AWS Linux (rule: Admin access)
 |    |-> Azure Linux (rule: Admin access)
 |-> SCA Policies
 |    |-> AWS Admin
 |    |-> AWS Dev
 |    |-> Azure Entra Admin
My Role2
 |-> Members
...
```

## Support & Roadmap

### Platform services
Identity graph will scan for role usage in the platform's services: 
- Identity
  - [x] Role members
  - [x] Web applications
- Privilege Cloud
  - [x] Safe members
- Secure Cloud Access
  - [x] Policy members
- Secure Infrastructure Access
  - [x] SIA Policies
- Conjur Cloud
  - [ ] Policy members
- [ ] Cloud Onboarding

### Commands
- `login file <filename>`: login with credentials stored in a file
- `enable <service>`: enable the service for scanning
- `ls services`: list enabled services
- `scan`: scan for roles and usage in services
- `ls roles`: list scanned roles
- `grep role <string>`: list roles that includes <string>
- `cat <role name> `: show role with the name <role name>
- `exit`: exit the program
## Installation

### Install python dependencies:
```bash
$ pip install requests
$ pip install python-dotenv
$ pip install asyncio
$ pip install aiohttp
$ pip install tqdm
```
NB: It is recommended to create a virtual env: `python -m venv /path/of/project`

### Authentication

Identity supports both interactive and file based authentication

#### File based authentication
Create the .env file:
```bash
TENANT_ID = 'my-tenant'
IDENTITY_ENDPOINT = 'https://abc1234.id.cyberark.cloud'
CLIENT_ID='identity-graph@cyberark.cloud.1234'
CLIENT_SECRET='P3s<w0rd'
```

Run this command:
```bash
[] # login file .env
Loading credentials from .env
Successfully logged in to tenant-name
```

## Usage

Run the program:
```
$ python3 main.py
[] # login file .env
Loading credentials from .env
Successfully logged in to tenant-name

[tenant-name] # enable all
All services enabled

[tenant-name] # scan
Please wait...
Loading Identity roles members: 100%|██████████| 102/102 [00:01<00:00, 92.55role/s]
Loading Identity roles webapps: 100%|██████████| 102/102 [00:01<00:00, 87.12role/s]
Loading Privilege Cloud safes members: 100%|██████████| 58/58 [00:02<00:00, 22.94safe/s]
Loading SIA policy members:: 100%|██████████| 7/7 [00:03<00:00,  1.88policy/s]
Loading SCA policy members: 100%|██████████| 9/9 [00:00<00:00,  9.63policy/s]
Scan complete!

[tenant-name] ls roles
My Role1
 |-> Members
 |    |-> Another role
 |    |-> some_user@cyberark.cloud.1234
 |-> Web Apps
 |    |-> My WebApp1
 |    |-> My WebApp2
 |    |-> My WebApp3
 |    |-> My WebApp4
 |-> Safes
 |    |-> Windows_Local_Users
 |    |-> Windows_Domain_Users
 |    |-> Linux_SSH_Users
 |-> SIA Policies
 |    |-> AWS Linux (rule: Admin access)
 |    |-> Azure Linux (rule: Admin access)
 |-> SCA Policies
 |    |-> AWS Admin
 |    |-> AWS Dev
 |    |-> Azure Entra Admin
My Role2
 |-> Members
 ...
```

## License

[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)