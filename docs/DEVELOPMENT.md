# Development — checkpoint 1: a running Python backend

This checkpoint demonstrates how HTTP requests become Python function calls and JSON responses. You already know Python; the new concepts are the web application, server process, routes, response contracts, and tooling.

## 1. Open the repository

Open `school-management-system-python` as a folder in VS Code. Use **Terminal → New Terminal** so commands start at the repository root, where the `scripts` folder is located.

```sh
python3.13 --version
```

This checkpoint supports the Python 3.13 series. On Windows, use `py -3.13` in place of `python3.13`. The version used by this project is selected explicitly rather than inherited from whichever `python` happens to be first on your computer's PATH.

## 2. Create the isolated environment

```sh
python3.13 scripts/bootstrap.py
```

The helper checks Python, installs the pinned uv dependency tool locally, and synchronizes the application packages from the committed lockfile. Rerun it after checking out dependency changes.

| Location | Purpose |
| --- | --- |
| `.tools/uv` | Isolated uv tooling, kept out of your existing Python installation |
| `apps/api/.venv` | Python environment and packages used by the API |
| `apps/api/pyproject.toml` | Dependencies, supported Python, and test/check settings |
| `apps/api/uv.lock` | Exact resolved package versions for reproducible installation |
| `.cache` | Local download caches |

Both environments and caches are ignored by Git. Other developers recreate them from the setup files. The first setup needs internet access. It does not replace system Python or create cloud resources.

`--frozen` synchronization installs the existing lockfile without choosing new versions. Deliberate dependency changes update the declaration and lockfile together. [uv project workflow](https://docs.astral.sh/uv/guides/projects/).

## 3. Read the application

Start with `apps/api/app/main.py`. It calls `create_app()` from `apps/api/app/application.py` to create the application object. The application factory sets the title/description and attaches the health router with `include_router`. Checkpoint 2 added settings, error handling, and a versioned learning router there. Routers let us organize future student, attendance, and finance endpoints into modules.

Next read `apps/api/app/api/health.py`. Its core behavior is:

```python
class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"

@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse()
```

`BaseModel` comes from Pydantic. The response model defines the JSON shape, and `Literal["ok"]` restricts the field to its documented value. The decorator connects an HTTP GET at `/health` to the Python function. FastAPI serializes the returned model as JSON.

This checks process liveness. Database readiness will be a separate check once persistence exists. [FastAPI first steps](https://fastapi.tiangolo.com/tutorial/first-steps/).

## 4. Run the server

```sh
python3.13 scripts/api.py dev
```

The helper uses the API's own virtual-environment interpreter and runs this command from `apps/api`:

```sh
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- `python -m uvicorn` runs the ASGI server using the selected environment.
- `app.main:app` imports the `app` object from `app/main.py`.
- `--reload` restarts the development server when source changes.
- `127.0.0.1` keeps it on your computer; `8000` is the port.

FastAPI defines the application; Uvicorn accepts network requests and runs it. Leave the terminal open and press Ctrl+C to stop the server. Reload mode is for development.

## 5. Send a request

Visit [process health](http://127.0.0.1:8000/health), or run in another terminal:

```sh
curl -i http://127.0.0.1:8000/health
```

Expect HTTP 200, a JSON content type, and `{"status":"ok"}`.

Trace it: browser/curl → Uvicorn → FastAPI router → Python function → Pydantic response → JSON → caller. You do not call the function manually for each visitor.

## 6. Explore the API documentation

Open [interactive documentation](http://127.0.0.1:8000/docs), expand **GET /health**, select **Try it out**, then **Execute**. Inspect the response body and status. The machine-readable API contract is at [OpenAPI JSON](http://127.0.0.1:8000/openapi.json).

The `/` address returns 404 because this checkpoint has no home-page route. Use `/docs` to explore the API. The Next.js interface will be added separately.

## 7. Use VS Code

Install the recommended Python, Python Debugger, and Ruff extensions. After setup, use **Python: Select Interpreter** in the Command Palette and select `apps/api/.venv` if needed. The repository provides an interpreter hint, test discovery, tasks, and a debugger configuration.

- **Terminal → Run Task → Python API: start** runs the reload server.
- **Terminal → Run Task → Python API: test** runs HTTP tests.
- **Run and Debug → Python API: debug FastAPI** runs a debug server without reload. Put a breakpoint on `return HealthResponse()`, request `/health`, inspect execution, and continue.

Stop an existing server before using the debugger because both use port 8000. [VS Code environments](https://code.visualstudio.com/docs/python/environments).

## 8. Check the work

```sh
python3.13 scripts/api.py check
```

This runs Ruff code checks, a formatting check, and pytest. The suite now covers health/documentation plus checkpoint 2's validation, settings, errors, and browser-origin behavior. It does not contact Neon, Firebase, or a database. Each test application is built with explicit settings so your local `.env` does not control the tested behavior.

Use `python3.13 scripts/api.py test` for tests only. Use `python3.13 scripts/api.py format` to apply automatic fixes/formatting, inspect the changes, and rerun checks. GitHub repeats setup and checks on Linux through the committed workflow.

Before moving on, explain the application object, server process, route decorator, response model, virtual environment, lockfile, and HTTP response. [Checkpoint 2](CHECKPOINT_02.md) adds request validation/settings; PostgreSQL models, sessions, and Alembic migrations follow.
