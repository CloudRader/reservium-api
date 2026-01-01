FROM python:3.13 as build

ENV HOME=/usr/src/app
ENV VENV_PATH=$HOME/.venv
ENV PATH="$VENV_PATH/bin:$PATH"

RUN apt-get update && apt-get install -y curl \
  && curl -LsSf https://astral.sh/uv/install.sh | sh

RUN mkdir -p $HOME
WORKDIR $HOME
RUN python -m venv $VENV_PATH

COPY pyproject.toml uv.lock ./
ENV UV=$HOME/.local/bin/uv
RUN $UV pip install --no-cache-dir -r pyproject.toml && $UV sync


FROM python:3.12-slim as runtime

ENV HOME=/usr/src/app
ENV VENV_PATH=$HOME/.venv
ENV PATH="$VENV_PATH/bin:$PATH"

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

RUN useradd --uid 8001 --user-group --home-dir $HOME --create-home app
WORKDIR $HOME
RUN mkdir output tmp

COPY --from=build $VENV_PATH $VENV_PATH

# copy source code
COPY reservation-app ./

WORKDIR $HOME/src

RUN chmod +x ../scripts/run_migrations.sh

ENTRYPOINT ["../scripts/run_migrations.sh"]
CMD ["python", "main.py"]
