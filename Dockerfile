# Build stage
FROM python:3.12.6-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --upgrade pip wheel "poetry==2.1.3"

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY app/app/  ./

WORKDIR /app/app/app

CMD ["python", "main.py"]
