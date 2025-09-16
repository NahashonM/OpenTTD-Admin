
# OpenTTD Admin Client
A tool to make it easier for OpenTTD Administrators to easily manage one or multiple servers.


# Usage

1. Install dependencies

```
pip install -r requirements.txt 
```

1. run client

```
python main.py
```


## .env file values
SERVER_IP			: openttd host
SERVER_PORT			: openttd admin port
ADMIN_CLIENT_NAME	    : client name
ADMIN_CLIENT_PASSWORD	: admin client password


## .env file sample

```
# --- GAME ---
SERVER_IP=myip
SERVER_PORT=myport

# --- ADMIN CLIENT ---
ADMIN_CLIENT_NAME=myadmin
ADMIN_CLIENT_PASSWORD=mypassword
```
