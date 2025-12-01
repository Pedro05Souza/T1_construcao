FROM python:3.12-slim-bullseye AS builder

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_VIRTUALENVS_PATH=/opt/poetry-venvs \
    POETRY_CACHE_DIR=/opt/poetry-cache

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN poetry install --only main --no-root


FROM python:3.12-slim-bullseye AS production

RUN pip install --upgrade pip poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_VIRTUALENVS_PATH=/opt/poetry-venvs

RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

ENV PYTHONPATH="/app/src"

COPY --from=builder /opt/poetry-venvs /opt/poetry-venvs
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY pyproject.toml poetry.lock* ./

RUN chown -R appuser:appuser /app && \
    chmod +x /app/scripts/*.py || true
USER appuser

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "t1_construcao.main:app", "--host", "0.0.0.0", "--port", "8000"]