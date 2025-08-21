# T1 Construção

## Setup

1. Install [Poetry](https://python-poetry.org/docs/#installation) if you haven't already.

2. Clone the repository and navigate to the project directory:
   ```bash
   cd T1_construcao
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

## Database Setup (Required before first run)

Before running the project for the first time, you need to set up the database migrations with aerich:

1. Make sure you have a `.env` file with your `DATABASE_URL` configured
2. Initialize aerich (if not already done):
   ```bash
   poetry run aerich init-db
   ```
3. If there are pending migrations, apply them:
   ```bash
   poetry run aerich upgrade
   ```

**Note:** The aerich configuration is already set up in `pyproject.toml`. You only need to run these commands once or when there are new migrations.

## Running the Project

To run the project, type this:
```bash
 docker compose up
```

## Running Tests

To run tests:
```bash
poetry run pytest
```

## Development

To add new dependencies:
```bash
poetry add <package-name>
```

To add development dependencies:
```bash
poetry add --group dev <package-name>
```

To see installed packages:
```bash
poetry show
```