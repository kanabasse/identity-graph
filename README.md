# Identity Graph - A CyberArk Identity role scanner 

Identity Graph is a role scanner, it discovers usage of roles in CyberArk services such as SIA, SCA and Privilege Cloud.
Roles are displayed with its associated services as such:

```bash
[INFO] My Role1
[INFO]  |-> Members
[INFO]  |    |-> Another role
[INFO]  |    |-> some_user@cyberark.cloud.1234
[INFO]  |-> Web Apps
[INFO]  |    |-> My WebApp1
[INFO]  |    |-> My WebApp2
[INFO]  |    |-> My WebApp3
[INFO]  |    |-> My WebApp4
[INFO]  |-> Safes
[INFO]  |    |-> Windows_Local_Users
[INFO]  |    |-> Windows_Domain_Users
[INFO]  |    |-> Linux_SSH_Users
[INFO]  |-> SIA Policies
[INFO]  |    |-> AWS Linux (rule: Admin access)
[INFO]  |    |-> Azure Linux (rule: Admin access)
[INFO]  |-> SCA Policies
[INFO]  |    |-> AWS Admin
[INFO]  |    |-> AWS Dev
[INFO]  |    |-> Azure Entra Admin
[INFO] My Role2
[INFO]  |-> Members
...
```

## Features
- [x] Threaded requests
- [x] Privilege Cloud Safes
- [x] SCA Policies
- [x] SIA Policies
- [x] Identity Webapps

## Installation

Create an .env file:
```bash
TENANT_ID = 'my-tenant'
IDENTITY_ENDPOINT = 'https://abc1234.id.cyberark.cloud'
CLIENT_ID='identity-graph@cyberark.cloud.1234'
CLIENT_SECRET='P3s<w0rd'
```

Install python libraries (dependencies):
```bash
$ pip install asyncio
$ pip install aiohttp
```

## Usage

Run the program:
```
$ python3 main.py
```

## License

[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)