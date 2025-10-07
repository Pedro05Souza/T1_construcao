# T1 Construção

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

## Infrastructure with Terraform

This project uses **Terraform** to automatically create and manage AWS infrastructure (such as EC2 instances and security groups).

### Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/downloads)
- Configured AWS credentials (Access Key and Secret Key)
---

### AWS CLI Setup

Before using Terraform, export your AWS credentials or configure them using `aws configure`.
```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_DEFAULT_REGION="us-east-1"
```
---

### Initializing Terraform

In the `infra/` directory, to download the required providers (such as AWS) and set up the environment, run:
```bash
terraform init
```

---

### Creating the Infrastructure

To apply the configuration and create the resources, run:
```bash
terraform apply
```
> Confirm by typing `yes` when prompted.

Terraform will create the EC2 instance and display its public IP address at the end of the process.

---

### 🧹 Destroying the Infrastructure

When you want to **delete all created resources**, run:
```bash
terraform destroy
```
> Confirm with `yes` to remove the resources from AWS.

---

