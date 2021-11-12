## Builder image
FROM python:3.8-alpine AS octoauth-builder

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev build-base

COPY requirements/prod.txt /tmp/requirements

RUN pip wheel -r /tmp/requirements --wheel-dir /dist/wheels

## Final image
FROM python:3.8-alpine

WORKDIR /octoauth

RUN addgroup -S octoauth && adduser -S octoauth -G octoauth

COPY requirements/prod.txt /octoauth/requirements
COPY --from=octoauth-builder /dist/wheels /octoauth/wheels

RUN apk add --no-cache libpq            \
    && pip install                      \
        --no-cache-dir                  \
        --no-index                      \
        --find-links=/octoauth/wheels   \
        -r requirements                 \
    && rm -rf /octoauth/wheels /octoauth/requirements

COPY octoauth /octoauth/octoauth

VOLUME /octoauth/assets

CMD [ "uvicorn", "--factory", "octoauth.webapp:OctoAuthASGI", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
