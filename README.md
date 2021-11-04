# OctoAuth

*Oauth2 provider that exposes a REST API for third-party applications*

## Contribute

**Requires**
- Python >= 3.8 / PIP (recommended to use virtualenv)

Install dependencies

```
pip install -r requirements/dev.txt
```

Run server in dev. mode using uvicorn (included in dependencies)

```
uvicorn --reload --factory octoauth.webapp:OctoAuthASGI
```
