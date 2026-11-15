# School management system — Python backend

A planned student management platform for multiple primary and secondary schools.

## Architecture

**Next.js → Python/FastAPI → Neon PostgreSQL**

- Python owns the HTTP API, school permissions, validation, business rules, persistence, migrations, integrations, and background jobs.
- Firebase Authentication handles sign-in and identity tokens; Python verifies identity and checks current school access.
- SQLAlchemy and psycopg provide database access; Alembic manages schema changes.
- Next.js with TypeScript provides the interface and calls the Python API for school data.

SQL Connect is not part of this architecture. This decision restores the original requirement that Python is responsible for the backend.

## Project status

Planning and learning documents are available. Application code, dependency files, cloud resources, and runnable commands will be added during the setup milestone.

## Start here

1. [Detailed implementation plan](docs/IMPLEMENTATION_PLAN.md)
2. [Initial development backlog](docs/BACKLOG.md)
3. [Python backend learning guide](docs/PYTHON_BACKEND_LEARNING_GUIDE.md)

## First implementation checkpoint

Open the repository in VS Code, select a supported Python interpreter, create the isolated environment, and run a small FastAPI endpoint. Explain the request lifecycle before introducing PostgreSQL, identity verification, and frontend integration.

Use only fictional data during development. Configuration examples and ignored-file rules will accompany the first application setup.
