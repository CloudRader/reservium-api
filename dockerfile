# build stage - conda takes a lot of memory (~1.4GB), so we will use it only
# in build stage, where it will create environment and export it to virtual environment,
# which will be used in the runtime image without conda memory overhead.
FROM continuumio/miniconda3 AS build-stage

ARG CONDA_ENV_NAME=buk-reservation

COPY environment-dev.yml .
RUN conda env create --file environment-dev.yml

RUN conda install -c conda-forge conda-pack

RUN conda-pack -n $CONDA_ENV_NAME -o /tmp/env.tar && \
  mkdir /venv && cd /venv && tar xf /tmp/env.tar && \
  rm /tmp/env.tar

RUN /venv/bin/conda-unpack && \
  tar cvzf venv.tar.gz /venv && \
  rm -rf /venv

# Runtime image, much more smaller than conda image
FROM docker.io/debian:buster AS runtime-stage

# Copy exported virtual environment from last build stage to this runtime image.
COPY --from=build-stage /venv.tar.gz .

WORKDIR /app

COPY app/app/ ./

SHELL ["/bin/bash", "-c"]

ENTRYPOINT  cd / && \
#  [ ! -d "venv" ] && tar xzf venv.tar.gz && rm venv.tar.gz || \
#  echo 'venv already extracted from tar' && \
  tar xzf venv.tar.gz && \
  source venv/bin/activate && \
  cd /app/app/app && \
  python -m main
