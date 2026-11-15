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

Checkpoints 1–2 implement a running FastAPI backend, validated request/response contracts, environment settings, safe errors with request IDs, exact browser-origin settings, and development-only learning endpoints. Local tooling, VS Code tasks/debugging, locked dependencies, and automated checks are included. PostgreSQL, authentication, school records, and the Next.js frontend follow in later checkpoints.

## Run the Python backend

From the repository root, using Python 3.13:

```sh
python3.13 scripts/bootstrap.py
python3.13 scripts/api.py dev
```

Setup installs tooling inside `.tools/uv` and application packages inside `apps/api/.venv`. It does not install packages into your existing Python environment. The first setup downloads dependencies; subsequent runs use the lockfile.

Open [interactive API documentation](http://127.0.0.1:8000/docs) or [process health](http://127.0.0.1:8000/health). The health response is `{"status":"ok"}`. Stop the development server with Ctrl+C.

To enable checkpoint 2's local learning endpoint, copy `apps/api/.env.example` to `apps/api/.env` once if you do not already have local settings, then restart the server. The `.env` file is ignored by Git. In the API docs, try **POST /api/v1/examples/student-validation** with fictional details. It validates input and returns `persisted: false`; no student record is created.

Application defaults disable learning endpoints. Staging/production reject debug or learning flags, require HTTPS for configured browser origins, and omit the public documentation/schema routes. CORS governs browser origins; school authentication and authorization are introduced in later checkpoints.

```sh
python3.13 scripts/api.py check
```

This checks Python code/formatting and runs the HTTP tests. A plain visit to `/` returns 404 because this checkpoint provides an API, with its documentation at `/docs`.

## VS Code

Open this repository folder and install its recommended Python/debugger extensions if needed. After setup, select `apps/api/.venv` as the Python environment. Run **Terminal → Run Task → Python API: start**, or use **Run and Debug → Python API: debug FastAPI**. Choose one server at a time because both use port 8000.

For the step-by-step explanation, start with [Development: checkpoint 1](docs/DEVELOPMENT.md).
Continue with [Checkpoint 2: requests, settings, and errors](docs/CHECKPOINT_02.md).

## Start here

1. [Detailed implementation plan](docs/IMPLEMENTATION_PLAN.md)
2. [Initial development backlog](docs/BACKLOG.md)
3. [Python backend learning guide](docs/PYTHON_BACKEND_LEARNING_GUIDE.md)

## Next checkpoint

Introduce local PostgreSQL, SQLAlchemy, and Alembic. Database-backed school records will then gain explicit identity and school-permission checks. Use only fictional records during development.
