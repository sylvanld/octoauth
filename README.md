# OctoAuth

*Oauth2 provider that exposes a REST API for third-party applications*

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
