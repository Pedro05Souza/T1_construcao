# T1 Construção - Service Appointment Management API

A RESTful API for managing service appointments with role-based access control (RBAC), built with FastAPI, PostgreSQL, and AWS Cognito authentication.

## Table of Contents

- [Domain Description](#domain-description)
- [Business Flows](#business-flows)
- [Environment Variables](#environment-variables)
- [Local Development](#local-development)
- [Running Migrations](#running-migrations)
- [Running Tests](#running-tests)
- [API Examples](#api-examples)
- [User Roles and Permissions](#user-roles-and-permissions)
- [CI/CD](#cicd)
- [Infrastructure](#infrastructure)

## Domain Description

This application manages a service appointment system with three core entities:

### Core Entities

1. **User**
   - Represents system users with different roles (admin, operator, client)
   - Each user has a unique ID, name, and role
   - Users can create and manage their own appointments

2. **Service**
   - Represents available services that can be booked
   - Contains: name, description, duration (in minutes), price, and active status
   - Only active services can be booked

3. **Appointment**
   - Represents a scheduled appointment linking a User to a Service
   - Contains: scheduled date/time, status (pending, confirmed, cancelled, completed), and optional notes
   - Validates scheduling conflicts and ensures appointments are in the future

### Relationships

- **User** ↔ **Appointment**: One-to-Many (a user can have multiple appointments)
- **Service** ↔ **Appointment**: One-to-Many (a service can have multiple appointments)
- **Appointment** requires both a User and a Service

## Business Flows

### 1. Appointment Management Flow

**Create Appointment:**
1. Client selects an available service
2. Client provides desired date/time
3. System validates:
   - Service exists and is active
   - Scheduled time is in the future
   - No scheduling conflicts exist
4. Appointment is created with status "pending"

**Confirm Appointment:**
1. Operator/Admin reviews pending appointments
2. Operator confirms the appointment
3. Status changes from "pending" to "confirmed"

**Cancel Appointment:**
1. Client, Operator, or Admin can cancel
2. Optional cancellation reason can be provided
3. Status changes to "cancelled"
4. Completed appointments cannot be cancelled

**Update Appointment:**
1. Client can update their own appointments (before confirmation/completion)
2. Admin/Operator can update any appointment
3. System re-validates scheduling conflicts if time is changed

### 2. Service Management Flow

**Create Service:**
1. Admin creates a new service with details (name, description, duration, price)
2. Service is created as active by default

**Update Service:**
1. Admin can update service details
2. Admin can activate/deactivate services
3. Inactive services cannot be booked

**List Services:**
1. Admin/Operator can list all services with filters (active status, name search)
2. Results are paginated

### 3. User Management Flow

**Create User:**
1. Admin creates users with name and role assignment
2. Default role is "client" if not specified

**List Users:**
1. Admin can list all users with filters (role, name search)
2. Results are paginated

**Update User:**
1. Admin can update any user
2. Users can update their own profile
3. Role changes require admin privileges

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=t1_construcao
POSTGRES_PORT=5432

# Database URL (used by application)
DATABASE_URL=postgres://postgres:postgres@localhost:5432/t1_construcao

# JWT Authentication (AWS Cognito)
JWT_ISSUER=https://your-cognito-domain.auth.region.amazoncognito.com
JWT_AUDIENCE=your-cognito-client-id

# Optional: Python Configuration
PYTHONUNBUFFERED=1
PYTHONPATH=/app/src
```

### Environment Variables Explained

- **POSTGRES_***: PostgreSQL database connection parameters
- **DATABASE_URL**: Full connection string for Tortoise ORM (used by the application)
- **JWT_ISSUER**: AWS Cognito User Pool issuer URL (found in Cognito console)
- **JWT_AUDIENCE**: AWS Cognito App Client ID (found in Cognito console)

## Local Development

### Prerequisites

- Python 3.12+
- Poetry (for dependency management)
- PostgreSQL 15+ (or use Docker Compose)
- Docker and Docker Compose (optional, for containerized setup)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd T1_construcao
   ```

2. **Install dependencies:**
   ```bash
   poetry install
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Running Locally

#### Option 1: Using Docker Compose (Recommended)

The `docker-compose.yml` is configured to:
- Start PostgreSQL database automatically
- Wait for database to be healthy
- Run migrations automatically (`aerich upgrade`)
- Start the FastAPI application

**Start everything:**
```bash
docker compose up
```

This will:
- ✅ Create and start PostgreSQL container
- ✅ Wait for database to be healthy
- ✅ Run migrations automatically
- ✅ Start API on port 8000

**Access points:**
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Useful commands:**
```bash
# Start in background
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down

# Stop and remove volumes (clean data)
docker compose down -v

# Rebuild after changes
docker compose up --build
```

#### Option 2: Using Makefile

```bash
# Complete setup and build
make build

# Run the application
make run

# Development mode with auto-reload
make run-dev
```

#### Option 3: Manual Setup

1. **Start PostgreSQL:**
   ```bash
   # Using Docker
   docker run -d \
     --name postgres \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=t1_construcao \
     -p 5432:5432 \
     postgres:15-alpine
   ```

2. **Run migrations:**
   ```bash
   poetry run aerich upgrade
   ```

3. **Start the application:**
   ```bash
   poetry run fastapi dev src/t1_construcao/main.py --host 0.0.0.0 --port 8000
   ```

## Running Migrations

### Using Aerich (Tortoise ORM migrations)

**Initialize migrations (first time only):**
```bash
poetry run aerich init-db
```

**Important:** The Aerich migration system will automatically generate migrations in the correct format when you run `aerich init-db`. The initial migration file has been removed to allow Aerich to generate it automatically with the correct format including all models (User, Service, Appointment).

**Create a new migration:**
```bash
poetry run aerich migrate "migration_name"
```

**Apply migrations:**
```bash
poetry run aerich upgrade
```

**Rollback last migration:**
```bash
poetry run aerich downgrade
```

**View migration status:**
```bash
poetry run aerich history
```

### Using Docker Compose

Migrations run automatically when starting with `docker compose up`. To run manually:

```bash
docker compose exec backend poetry run aerich upgrade
```

**Note:** Migrations are automatically generated on first run. The `docker-compose.yml` is configured to:
1. Wait for database to be ready
2. Run `aerich init-db` (creates initial migration if needed)
3. Run `aerich upgrade` (applies all migrations)
4. Start the API server

## Running Tests

### Test Database Setup

The project uses **PostgreSQL** for both development and testing. A separate test database container is available in `docker-compose.yml`.

**Start the test database:**
```bash
# Using Docker Compose
docker compose up -d test_db

# Or using Makefile
make test-db-up
```

The test database will be available at:
- **Host:** `localhost`
- **Port:** `5433` (default, configurable via `POSTGRES_TEST_PORT`)
- **Database:** `t1_construcao_test`
- **User:** `postgres` (default)
- **Password:** `postgres` (default)

### Run all tests:
```bash
poetry run pytest
```

### Run tests with Docker test database:
```bash
# Set the test database URL
export TEST_DATABASE_URL=postgres://postgres:postgres@localhost:5433/t1_construcao_test

# Run tests
poetry run pytest

# Or use the Makefile command (starts test_db automatically)
make test-all
```

### Run with coverage:
```bash
poetry run pytest --cov=src --cov-report=term --cov-report=html
```

### Run specific test file:
```bash
poetry run pytest tests/test_user_controller.py
```

### Run with verbose output:
```bash
poetry run pytest -v
```

### Run integration tests (requires test database):
```bash
# Start test database first
make test-db-up

# Run integration tests
make test-integration
```

### Using Makefile:
```bash
# Start test database
make test-db-up

# Run all tests (unit + integration) with Docker test database
make test-all

# Run only unit tests (no database required)
make test

# Run tests with coverage
make test-coverage

# Run tests with verbose output
make test-verbose
```

## API Examples

### Authentication

All API endpoints (except `/`) require a valid JWT Bearer token. Get your token from AWS Cognito and include it in the `Authorization` header:

```bash
Authorization: Bearer <your-jwt-token>
```

### Base URL

```
http://localhost:8000/api/v1
```

### User Management

#### List Users (Admin only)
```bash
curl -X GET "http://localhost:8000/api/v1/users?page=1&page_size=10&role=admin" \
  -H "Authorization: Bearer <admin-token>"
```

#### Create User (Admin only)
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "role": "client"
  }'
```

#### Get User by ID (Admin or self)
```bash
curl -X GET "http://localhost:8000/api/v1/users/{user_id}" \
  -H "Authorization: Bearer <token>"
```

#### Update User (Admin or self)
```bash
curl -X PUT "http://localhost:8000/api/v1/users/{user_id}" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Updated",
    "role": "operator"
  }'
```

#### Delete User (Admin only)
```bash
curl -X DELETE "http://localhost:8000/api/v1/users/{user_id}" \
  -H "Authorization: Bearer <admin-token>"
```

### Service Management

#### List Services (Admin/Operator)
```bash
curl -X GET "http://localhost:8000/api/v1/services?is_active=true&page=1&page_size=10" \
  -H "Authorization: Bearer <operator-token>"
```

#### Create Service (Admin only)
```bash
curl -X POST "http://localhost:8000/api/v1/services" \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Haircut",
    "description": "Professional haircut service",
    "duration_minutes": 30,
    "price": "25.00"
  }'
```

#### Get Service by ID (Admin/Operator)
```bash
curl -X GET "http://localhost:8000/api/v1/services/{service_id}" \
  -H "Authorization: Bearer <operator-token>"
```

#### Update Service (Admin only)
```bash
curl -X PUT "http://localhost:8000/api/v1/services/{service_id}" \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Premium Haircut",
    "price": "35.00",
    "is_active": true
  }'
```

### Appointment Management

#### List Appointments
```bash
# Admin/Operator: see all appointments
curl -X GET "http://localhost:8000/api/v1/appointments?status=pending&page=1" \
  -H "Authorization: Bearer <operator-token>"

# Client: see only own appointments (automatically filtered)
curl -X GET "http://localhost:8000/api/v1/appointments" \
  -H "Authorization: Bearer <client-token>"
```

#### Create Appointment (Client/Operator/Admin)
```bash
curl -X POST "http://localhost:8000/api/v1/appointments" \
  -H "Authorization: Bearer <client-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": "service-uuid",
    "scheduled_at": "2024-12-25T10:00:00Z",
    "notes": "Please arrive 10 minutes early"
  }'
```

#### Get Appointment by ID
```bash
curl -X GET "http://localhost:8000/api/v1/appointments/{appointment_id}" \
  -H "Authorization: Bearer <token>"
```

#### Update Appointment (Owner or Admin/Operator)
```bash
curl -X PUT "http://localhost:8000/api/v1/appointments/{appointment_id}" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "scheduled_at": "2024-12-25T11:00:00Z",
    "notes": "Updated notes"
  }'
```

#### Confirm Appointment (Operator/Admin only)
```bash
curl -X POST "http://localhost:8000/api/v1/appointments/{appointment_id}/confirm" \
  -H "Authorization: Bearer <operator-token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### Cancel Appointment (Owner or Admin/Operator)
```bash
curl -X POST "http://localhost:8000/api/v1/appointments/{appointment_id}/cancel" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Client requested cancellation"
  }'
```

#### Delete Appointment (Owner or Admin/Operator)
```bash
curl -X DELETE "http://localhost:8000/api/v1/appointments/{appointment_id}" \
  -H "Authorization: Bearer <token>"
```

## User Roles and Permissions

### Role: `admin`

**Full system access:**
- ✅ Create, read, update, delete users
- ✅ Create, read, update, delete services
- ✅ View all appointments
- ✅ Confirm appointments
- ✅ Cancel any appointment
- ✅ Update any appointment

**Example user:**
```json
{
  "name": "System Administrator",
  "role": "admin",
  "cognito:groups": ["admin"]
}
```

### Role: `operator`

**Service and appointment management:**
- ❌ Cannot manage users
- ✅ View all services
- ✅ View all appointments
- ✅ Confirm appointments
- ✅ Cancel any appointment
- ✅ Update any appointment

**Example user:**
```json
{
  "name": "Service Operator",
  "role": "operator",
  "cognito:groups": ["operator"]
}
```

### Role: `client`

**Self-service appointment management:**
- ❌ Cannot manage users
- ❌ Cannot manage services
- ✅ View own appointments only
- ✅ Create appointments
- ✅ Update own appointments
- ✅ Cancel own appointments
- ✅ View own user profile

**Example user:**
```json
{
  "name": "John Client",
  "role": "client",
  "cognito:groups": ["client"]
}
```

### Permission Matrix

| Action | Admin | Operator | Client |
|--------|-------|----------|--------|
| List Users | ✅ | ❌ | ❌ |
| Create User | ✅ | ❌ | ❌ |
| Update Own User | ✅ | ❌ | ✅ |
| Update Other User | ✅ | ❌ | ❌ |
| Delete User | ✅ | ❌ | ❌ |
| List Services | ✅ | ✅ | ❌ |
| Create Service | ✅ | ❌ | ❌ |
| Update Service | ✅ | ❌ | ❌ |
| Delete Service | ✅ | ❌ | ❌ |
| List All Appointments | ✅ | ✅ | ❌ |
| List Own Appointments | ✅ | ✅ | ✅ |
| Create Appointment | ✅ | ✅ | ✅ |
| Update Own Appointment | ✅ | ✅ | ✅ |
| Update Other Appointment | ✅ | ✅ | ❌ |
| Confirm Appointment | ✅ | ✅ | ❌ |
| Cancel Own Appointment | ✅ | ✅ | ✅ |
| Cancel Other Appointment | ✅ | ✅ | ❌ |
| Delete Own Appointment | ✅ | ✅ | ✅ |
| Delete Other Appointment | ✅ | ✅ | ❌ |

## CI/CD

The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that:

- **Runs on:** Push/PR to `main` and `develop` branches
- **Automated testing:** Runs all tests with PostgreSQL service
- **Code quality checks:** Linting, formatting, type checking
- **Coverage reporting:** Generates coverage reports and JUnit XML
- **Docker build:** Builds Docker images on main branch

### CI Pipeline Steps

1. Checkout code
2. Set up Python 3.12
3. Install Poetry
4. Install dependencies
5. Wait for PostgreSQL
6. Run database migrations
7. Run code quality checks
8. Run tests with coverage

### Makefile Commands for CI

```bash
# Complete CI build pipeline
make ci-build

# Run CI tests
make ci-test

# Build Docker images
make docker-build
```

## Infrastructure

### Terraform

This project uses **Terraform** to automatically create and manage AWS infrastructure.

#### Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/downloads)
- Configured AWS credentials

#### AWS CLI Setup

```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_DEFAULT_REGION="us-east-1"
```

#### Initialize Terraform

```bash
cd infra/
terraform init
```

#### Create Infrastructure

```bash
terraform apply
# Confirm with 'yes'
```

#### Destroy Infrastructure

```bash
terraform destroy
# Confirm with 'yes'
```

## Development

### Adding Dependencies

```bash
# Production dependency
poetry add <package-name>

# Development dependency
poetry add --group dev <package-name>
```

### Viewing Installed Packages

```bash
poetry show
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type check
make type-check

# Run all checks
make check
```

## Additional Resources

- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Alternative Docs:** http://localhost:8000/redoc (ReDoc)
- **OpenAPI Schema:** http://localhost:8000/openapi.json

## License

MIT
