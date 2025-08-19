FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/opt/poetry-cache

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry install --without dev --no-root

FROM python:3.12-slim AS production

# Install Poetry in production stage
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/opt/poetry-cache

COPY --from=builder /opt/poetry-cache/virtualenvs /opt/poetry-cache/virtualenvs

ENV PATH="/opt/poetry-cache/virtualenvs/t1-construcao-9TtSrW0h-py3.12/bin:$PATH"

WORKDIR /app

# Copy application code
COPY src/ ./src/

# Set PYTHONPATH to include the src directory
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Set working directory to the correct location
WORKDIR /app

EXPOSE 8000

CMD ["fastapi", "dev", "src/t1_construcao/main.py", "--host", "0.0.0.0"]