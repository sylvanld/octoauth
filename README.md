# OctoAuth

*Oauth2 provider that exposes a REST API for third-party applications*

## Configuration

OctoAuth API can be configured using environment variables.

|Variable|Description|Default value|
|-|-|-|
|ACCOUNT_DASHBOARD_URL|**REQUIRED**. URL of [octoauth accounts dashboard](https://github.com/sylvanld/octoauth-dashboard) which allows users to manage their account preferences and personal data.|-|
|OCTOAUTH_DATABASE_URL|**REQUIRED**. [URL used by sqlalchemy](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) to connect to OctoAuth database.|-|
|OCTOAUTH_MAILING_ENABLED|Boolean defining whether email must be sent to notify users, for example when account is created, etc..|false|

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
