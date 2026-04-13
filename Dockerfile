FROM python:3.14-slim

ENV HOME=/usr/src/app
ENV VENV_PATH=$HOME/.venv
ENV PATH="$VENV_PATH/bin:$PATH"

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
 && rm -rf /var/lib/apt/lists/* \
 && curl -LsSf https://astral.sh/uv/install.sh | sh

RUN useradd --uid 8001 --user-group --home-dir $HOME --create-home app
WORKDIR $HOME

RUN python -m venv $VENV_PATH

COPY pyproject.toml uv.lock ./
RUN $HOME/.local/bin/uv sync --frozen --no-dev

# copy source code
COPY reservation-app ./

WORKDIR $HOME/src

RUN chmod +x ../scripts/run_migrations.sh

ENTRYPOINT ["../scripts/run_migrations.sh"]
CMD ["python", "main.py"]