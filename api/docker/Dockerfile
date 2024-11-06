FROM python:3.11-slim as base
ENV PYTHONUNBUFFERED 0

WORKDIR /app

FROM base as build-phase

COPY requirements.txt .
COPY requirements-gradio.txt .
COPY pyproject.toml .
COPY src src/

RUN apt update && apt -y install gcc g++

RUN pip install --upgrade pip
RUN pip install keyrings.tmp.gcp_artifact_registry_auth
ARG PIP_EXTRA_CREDENTIALS
ARG PIP_EXTRA_INDEX_URL="https://${PIP_EXTRA_CREDENTIALS}asia-python.pkg.dev/recursive-research-core/recursive-common-pypi/simple/ https://download.pytorch.org/whl/cpu"
RUN pip install --no-cache-dir -t packages ".[core,gradio]"

ENV PYTHONPATH packages

FROM base as execution-phase

COPY --from=build-phase /app/packages packages
ENV PYTHONPATH packages
COPY config config/

#CMD python -u -m uvicorn recursiveai.findflow.customer_service.app:create_app --factory --proxy-headers --host 0.0.0.0 --port 8000
CMD python -u -m uvicorn recursiveai.findflow.customer_service.app:create_gradio_app --factory --proxy-headers --host 0.0.0.0 --port 8080
