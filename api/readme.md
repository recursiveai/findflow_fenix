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

### Tika Server Docker Image

Preferably build the image from [tika_docker](https://github.com/recursiveai/tika-docker) repository.

Alternatively pull image from `platform-findflow`.

```
gcloud auth configure-docker asia-northeast1-docker.pkg.dev

docker pull asia-northeast1-docker.pkg.dev/platform-findflow/findflow/tika-server:2.8.0

docker tag asia-northeast1-docker.pkg.dev/platform-findflow/findflow/tika-server:2.8.0 tika-server
```

### Dependencies

Icarus depends on `Postgres`, `Elasticsearch` and `Tika`.
Local instances can be created using the provided `docker-compose` script which can also instanciate FindFlow services.

```
docker-compose -f docker/docker-compose.yaml up
```

### Services

Run the services directly from the commandline.

#### FindFlow Discovery

```bash
export FF__CONFIG_FILE_PATH=config/local/discovery_config.yaml
export OPENAI_API_KEY=<OPENAI_API_KEY>
python -u -m uvicorn recursiveai.findflow.discovery.app:run_app --factory --proxy-headers --host 0.0.0.0 --port 8002
```

To use Azure's OpenAI offering set the following environment variables and the corresponding api key.

```bash
export FF__CONFIG_FILE_PATH=config/local/discovery_config.yaml
export AZURE_API_KEY=<AZURE_API_KEY>
export AZURE_API_TYPE=azure
export AZURE_API_BASE=https://findflow-azure-openai.openai.azure.com
export AZURE_API_VERSION="2024-02-01"
```

Reverting back to OpenAI endpoint requires unsetting the environment variables.

```bash
unset AZURE_API_TYPE
unset AZURE_API_BASE
unset AZURE_API_VERSION
```

#### FindFlow Support

```bash
export FF__CONFIG_FILE_PATH=config/local/support_config.yaml
python -u -m uvicorn recursiveai.findflow.support.app:run_app --factory --proxy-headers --host 0.0.0.0 --port 8003
```

#### FindFlow Worker

To simulate the worker job on prod, trigger it each time you want to run it (recommended):

```bash
export FF__CONFIG_FILE_PATH=config/local/worker_config.yaml
export OPENAI_API_KEY=<OPENAI_API_KEY>
python -u -m recursiveai.findflow.worker.job
```

To trigger it with an API call:

```bash
export FF__CONFIG_FILE_PATH=config/local/worker_config.yaml
export OPENAI_API_KEY=<OPENAI_API_KEY>
python -u -m uvicorn recursiveai.findflow.worker.app:run_app --factory --proxy-headers --host 0.0.0.0 --port 8004
```

To use Azure's OpenAI offering set the following environment variables and the corresponding api key.

```bash
export FF__CONFIG_FILE_PATH=config/local/worker_config.yaml
export AZURE_API_KEY=<AZURE_API_KEY>
export AZURE_API_TYPE=azure
export AZURE_API_BASE=https://findflow-azure-openai.openai.azure.com
export AZURE_API_VERSION="2024-02-01"
```

Reverting back to OpenAI endpoint requires unsetting the environment variables.

```bash
unset AZURE_API_TYPE
unset AZURE_API_BASE
unset AZURE_API_VERSION
```

### FindFlow Worker - Webcrawler

To emulate the webcrawler in production, run the following command:

```bash
export FF__CONFIG_FILE_PATH=config/local/webcrawler_config.yaml
python -u -m recursiveai.findflow.worker.webcrawler.job
```

For testing the webcrawler, run the following command:

```bash
export FF__CONFIG_FILE_PATH=config/local/webcrawler_config.yaml
python -u -m uvicorn src.recursiveai.findflow.worker.webcrawler.app:run_app --factory --proxy-headers --host 0.0.0.0 --port 8004
```

### Research

Run the example script as follow (change configuration as needed):

```bash
python -m recursiveai.findflow.research.example
```

## Docker Images

Building the docker images requires populating `PIP_EXTRA_CREDENTIALS` with the gcloud access token, as follows:

```
export PIP_EXTRA_CREDENTIALS=oauth2accesstoken:`gcloud auth print-access-token`@
```

Note that the previous token is only valid for an hour.

#### FindFlow Discovery

Build discovery's docker image:

```
docker build -f docker/discovery.Dockerfile \
-t discovery --build-arg PIP_EXTRA_CREDENTIALS=$PIP_EXTRA_CREDENTIALS .
```

#### FindFlow Support

Build support's docker image:

```
docker build -f docker/support.Dockerfile \
-t support --build-arg PIP_EXTRA_CREDENTIALS=$PIP_EXTRA_CREDENTIALS .
```

#### FindFlow Worker

Build worker's docker image:

```
docker build -f docker/worker.Dockerfile \
-t worker --build-arg PIP_EXTRA_CREDENTIALS=$PIP_EXTRA_CREDENTIALS .
```

#### Docker Compose

Run FindFlow locally via docker-compose.

```
docker-compose -f docker/docker-compose.yaml up
```

## Troubleshooting

You may see this warning while running a tokenizer:

`Token indices sequence length is longer than the specified maximum sequence length for this model...`

If the tokens are only used for chunking sentences, then this warning can safely be ignored. However, if the tokens are to be put into a batch and fed into a model (e.g., to the Contriever model), then the model will crash.

---

If you encounter: `RuntimeError: OCR initialisation failed` when running index_example.py, you can try:

- `brew install tesseract-lang`
- `brew --prefix tesseract-lang` to get the path where tesseract-lang is installed on your system
- copy and paste the path to `tesseract_data_path` in `./config/local/worker_config.yaml`

---

If you encounter this specific issue during `make install`

```
[nltk_data] Error loading punkt: <urlopen error [SSL:
[nltk_data]     CERTIFICATE_VERIFY_FAILED] certificate verify failed:
[nltk_data]     unable to get local issuer certificate (_ssl.c:1007)>
```

please run this

```
sh "/Applications/Python 3.10/Install Certificates.command"
```

[(Stackoverflow source)](https://stackoverflow.com/questions/76448630/error-related-to-nltk-downloadstopwords)

## Benchmarking

See [benchmarking documentation](/docs/benchmarking.md).
