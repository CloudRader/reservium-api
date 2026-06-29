# ==========================================
# Build Stage
# ==========================================
FROM python:3.14.6-slim-trixie AS build

# Copy uv binary directly from official image
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /bin/
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    HOME=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR $HOME

# Cache dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --locked --no-editable --no-install-project

# ==========================================
# Runtime Stage
# ==========================================
FROM python:3.14.5-slim-trixie AS runtime

ENV HOME=/app \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create unprivileged system user without unnecessary defaults
RUN useradd --uid 8001 --user-group --system --home-dir $HOME app

WORKDIR $HOME

# Copy artifacts with correct ownership immediately
COPY --from=build --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app src ./src
COPY --chown=app:app scripts/run_migrations.sh ./scripts/run_migrations.sh
COPY --chown=app:app alembic.ini .

WORKDIR $HOME

RUN chmod +x scripts/run_migrations.sh

USER app

ENTRYPOINT ["scripts/run_migrations.sh"]
CMD ["python", "src/main.py"]
