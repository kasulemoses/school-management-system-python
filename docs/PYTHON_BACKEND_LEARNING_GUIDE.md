# Learning Python as a web backend

You already know Python. These checkpoints focus on web/backend concepts and use the student management system as the example. The first runnable checkpoint is documented in [Development](DEVELOPMENT.md), followed by [request validation and settings](CHECKPOINT_02.md). Persistence and later sections describe upcoming work.

## How each session works

Explain the purpose and vocabulary, show one small change, run it, inspect the request/response or database result, and connect the change to the whole application. You should be able to explain the behavior before we move to the next major concept.

## 1. Runtime and environment

Distinguish the Python interpreter, virtual environment, installed packages, application source, configuration, and server process. We will select a compatible interpreter and make VS Code use the project's environment. A virtual environment isolates packages; it does not host PostgreSQL.

**Checkpoint:** Identify which Python runs the backend and where dependencies are installed.

## 2. HTTP and the first endpoint

Learn method, URL, path/query parameters, headers, body, response status, and JSON. FastAPI maps a request to a Python function. Uvicorn runs the application as an ASGI server. Explore FastAPI's interactive `/docs` and inspect a real response.

Illustrative first endpoint, to be implemented during setup:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get('/health')
def health_check():
    return {'status': 'ok'}
```

**Checkpoint:** Explain how a browser request triggers the function without calling it directly yourself.

## 3. Request/response validation

Pydantic schemas describe accepted input and returned output. Compare a valid student submission with missing/invalid data and protected fields. Separate input schemas from database models; a caller must not be allowed to set their own permissions or school ownership.

**Checkpoint:** Trace where invalid input is rejected and explain why frontend validation is additional feedback.

## 4. Routing, dependencies, and services

Organize domain routers, share settings/identity/database dependencies, and keep business actions in services. Start synchronously so blocking database and Firebase calls use the framework's synchronous execution path. Discuss async after understanding the actual I/O behavior.

**Checkpoint:** Trace request → dependency checks → service → response; identify which layer owns a business rule.

## 5. Persistence and migrations

PostgreSQL stores records. psycopg is the driver, SQLAlchemy maps/queries them, a session manages unit-of-work state, and Alembic changes the schema across releases. Use a real PostgreSQL development/test environment.

**Checkpoint:** Create a schema through migrations, save a fictional record, restart the API, and retrieve it.

## 6. Authentication and authorization

Firebase establishes identity. Python verifies the ID token and loads current school permissions from PostgreSQL. An authenticated user can still be forbidden from a school or action. Avoid rebuilding password handling or trusting a browser role value.

**Checkpoint:** Two identities call the same endpoint; one succeeds and the other is rejected for a clear reason.

## 7. Transactions, constraints, and concurrency

Registration can create related student/enrollment/audit records. A transaction makes related changes commit or roll back together. Constraints and locking/conditional updates address duplicate or concurrent requests. A pre-check alone does not eliminate races.

**Checkpoint:** Force a failure and demonstrate rollback; submit duplicates and inspect the conflict result.

## 8. Frontend integration

Next.js signs in, obtains an ID token through Firebase's SDK, sends requests to Python, and handles errors. CORS controls permitted browser origins; it is not user authorization. All school data still flows through the API.

**Checkpoint:** Trace a student form from browser network request to Python service, database write, and rendered response.

## 9. Tests and troubleshooting

Use focused unit tests for pure rules, HTTP integration tests for API/auth behavior, and PostgreSQL integration tests for constraints/transactions. Test other-school access directly. Inspect safe logs and request IDs without exposing tokens or student data.

**Checkpoint:** Explain what a failing test proves and reproduce the failure through a request.

## 10. Deployment and durable jobs

Separate local/staging/production configuration, apply migrations once per release, configure database pools, and monitor errors. Reports/imports/notifications needing reliable retries go to a Python worker with durable job records. An API process restart must not silently lose critical work.

**Checkpoint:** Explain where API, database, files, worker, secrets, and backups live, and how a release is recovered.

## First implementation session

Checkpoint 1 now provides Python 3.13 setup, a VS Code workspace configuration, and a running health endpoint. Follow [Development](DEVELOPMENT.md) to inspect each command and trace a request before introducing PostgreSQL, authentication, or the frontend.

References: [FastAPI first steps](https://fastapi.tiangolo.com/tutorial/first-steps/), [FastAPI application structure](https://fastapi.tiangolo.com/tutorial/bigger-applications/), [Database integration](https://fastapi.tiangolo.com/tutorial/sql-databases/), [Firebase token verification](https://firebase.google.com/docs/auth/admin/verify-id-tokens).
