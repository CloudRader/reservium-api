# build stage - conda takes a lot of memory (~1.4GB), so we will use it only
# in build stage, where it will create environment and export it to virtual environment,
# which will be used in the runtime image without conda memory overhead.
FROM docker.io/condaforge/mambaforge:latest AS build-stage

ARG CONDA_ENV_NAME=buk-reservation

COPY conda-lock.yml ./
RUN mamba install conda-pack conda-lock

RUN conda-lock install -n $CONDA_ENV_NAME conda-lock.yml && \
    mamba clean --all --yes && \
    conda-pack -n $CONDA_ENV_NAME -o /tmp/env.tar && \
    mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
    rm /tmp/env.tar

# Runtime image, much more smaller than conda image
FROM do AS runtime-stage

WORKDIR /app

# Copy exported virtual environment from last build stage to this runtime image.
COPY --from=build-stage /venv /venv

COPY app/app ./app/


SHELL ["/bin/bash", "-c"]

ENTRYPOINT source /venv/bin/activate && cd app/app/ && \
python -m main