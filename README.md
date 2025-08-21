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

## Build & Run Scripts (Makefile)

This project includes a comprehensive Makefile for easy development and CI/CD integration. To see all available commands:

```bash
make help
```

### Quick Start Commands

- **Complete setup and build:**
  ```bash
  make build
  ```

- **Fresh start (clean setup):**
  ```bash
  make fresh-start
  ```

- **Run the application:**
  ```bash
  make run
  ```

- **Development mode:**
  ```bash
  make run-dev
  ```

### Key Commands for CI/CD

- **CI build pipeline:**
  ```bash
  make ci-build
  ```

- **Run tests with coverage:**
  ```bash
  make test-coverage
  ```

- **Code quality checks:**
  ```bash
  make check
  ```

## Running the Project

### Using Make (Recommended)
```bash
make run
```

### Using Docker Compose directly
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

## CI/CD Integration

The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that uses the Makefile commands:

- **Automated testing** on push/PR to main branch
- **Code quality checks** (linting, formatting, type checking)
- **Coverage reporting** with artifact uploads
- **Docker image building** for production

The CI pipeline uses these Makefile commands:
- `make ci-build` - Complete CI build pipeline
- `make ci-test` - Run tests with coverage and JUnit output
- `make docker-build` - Build Docker images