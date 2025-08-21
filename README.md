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

## Running the Project

To run the project, type this:
```bash
 cd src/t1_construcao && poetry run fastapi dev main.py
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