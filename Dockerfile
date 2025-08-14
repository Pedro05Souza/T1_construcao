FROM python:3.12-slim as builder

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pipx install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/opt/poetry-cache

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-dev && rm -rf $POETRY_CACHE_DIR

FROM python:3.12-slim as production

RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy application code
COPY src/ ./src/

EXPOSE 8000

CMD ["poetry", "run", "dev", "src/t1_construcao/main.py"]