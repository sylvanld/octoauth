# OctoAuth

*Oauth2 provider that exposes a REST API for third-party applications*

## Contribute

Install dependencies

```
pip install -r requirements/dev.txt
```

Run server in dev. mode using uvicorn (included in dependencies)

```
uvicorn --reload --factory octoauth.webapp:OctoAuthASGI
```
