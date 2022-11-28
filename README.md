# OctoAuth

*Oauth2 provider that exposes a REST API for third-party applications*

## Configuration

OctoAuth API can be configured using environment variables. 

**This is also true when using docker image.**

|Variable|Description|Default value|
|-|-|-|
|OCTOAUTH_DASHBOARD_URL|**REQUIRED**. URL of [octoauth accounts dashboard](https://github.com/sylvanld/octoauth-dashboard) which allows users to manage their account preferences and personal data.|-|
|OCTOAUTH_DATABASE_URL|**REQUIRED**. [URL used by sqlalchemy](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) to connect to OctoAuth database.|-|
|OCTOAUTH_MAILING_ENABLED|Boolean defining whether email must be sent to notify users, for example when account is created, etc..|false|
|OCTOAUTH_JWT_PRIVATE_KEY|Path to an RSA private key [used to sign JWT](#jwt-private-key). If running OctoAuth in docker, don't forget to put it in a volume.|`assets/private-key.pem` (path is relative to `/octoauth` in docker image)|

### JWT Private key

A private key is required to encode JSON Web Tokens using algorithm `RSA256`. This allow client to decode tokens without knowing encryption key nor making request to OctoAuth server, and those improve authentication system's scalability. A private key might be generated using `openssl` with the following command

```bash
mkdir assets/
openssl genrsa -out assets/private-key.pem 4096
```

## Contribute

**Requires**
- Python >= 3.8 / PIP (recommended to use virtualenv)
- make

To install psycopg2 (in dependencies) you need `libpq-dev`. It can be installed on ubuntu with

```bash
sudo apt install -y libpq-dev
```

Install dependencies

```bash
pip install -r requirements/dev.txt
```

Run server in dev. mode using uvicorn (included in dependencies)

```bash
uvicorn --reload --factory octoauth.webapp:OctoAuthASGI
```

Before publishing a merge request, please clean/format your code using

```bash
make format
```
