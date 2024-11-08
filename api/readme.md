# FindFlow Assistant - API

FindFlow Assistant's API services and tools.

## Development

Set local Python version to `3.11` using pyenv.

```
pyenv local 3.11
```

### Python virtual environment

Create and load a virtual environement.

```
python -m kantan .venv
source .venv/bin/activate
```

### Install

Install all dependencies in editable mode.

```
make install
```

Install pre-commit hooks.

```
pre-commit install
```

### Help

Check what other shortcuts are available.

```
make help
```

## Local Deployment

### Dependencies

FindFlow Assistant API depends on `Postgres` and `Elasticsearch`.
Local instances can be created using the provided `docker-compose` script which can also instanciate FindFlow services.

```
podman compose -f docker/docker-compose.yaml up
```

Populate and update database to latest schema.

```
python -m alembic upgrade head
```

###  Services

Run the services directly from the commandline.

#### FindFlow Assistant API

```bash
META__CONFIG_FILE_PATH=config/local/api_config.yaml \
python -u -m uvicorn \
recursiveai.findflow.assistant.api.app:run_app \
--factory --proxy-headers \
--host localhost --port 8001
```

#### Using Identity Platform

In order to use an Identity Platform setup from a GCP project gcloud needs to be setup.

```bash
gcloud auth application-default login
gcloud config set project <project-id|dev-findflow>
gcloud auth application-default set-quota-project <project-id|dev-findflow>
```

## Docker Images

Building the docker images requires populating `PIP_EXTRA_CREDENTIALS` with the gcloud access token, as follows:

```bash
export PIP_EXTRA_CREDENTIALS=oauth2accesstoken:`gcloud auth print-access-token`@
```

Note that the previous token is only valid for an hour.


#### FindFlow Assistant API

Build api's docker image:

```
docker build -f docker/support.Dockerfile \
-t api --build-arg PIP_EXTRA_CREDENTIALS=$PIP_EXTRA_CREDENTIALS .
```
