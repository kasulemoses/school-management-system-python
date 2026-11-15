# Checkpoint 2 — validated requests, settings, and errors

Python now accepts a JSON request, validates its fields, and returns a defined response. This checkpoint uses fictional student details without registering a student or accessing a database.

## Run this checkpoint

From the repository root:

```sh
python3.13 scripts/bootstrap.py
```

If you do not already have `apps/api/.env`, copy `apps/api/.env.example` to that path. Preserve existing local settings. The example enables learning endpoints and allows the two explicit local Next.js origins. The local `.env` is ignored by Git.

Restart the server after changing settings:

```sh
python3.13 scripts/api.py dev
```

Open [API documentation](http://127.0.0.1:8000/docs) and expand **POST /api/v1/examples/student-validation**. Use **Try it out** and submit:

```json
{
  "first_name": "  Amina  ",
  "last_name": "Example",
  "admission_number": "DEMO-0042"
}
```

Expected response: HTTP 200 and:

```json
{
  "valid": true,
  "persisted": false,
  "student": {
    "first_name": "Amina",
    "last_name": "Example",
    "admission_number": "DEMO-0042"
  }
}
```

HTTP 200 means the validation operation succeeded. We do not return 201 because no student resource was created. A real admission workflow will later check identity, school permissions, uniqueness, and database consistency.

## Follow the Python request lifecycle

1. `app/main.py` is Uvicorn's entry point. It calls `create_app()` from `app/application.py`.
2. `app/core/settings.py` loads and validates configuration. The application factory decides which routes and browser origins to enable.
3. The outer request middleware assigns a server-generated request ID.
4. `app/api/v1/router.py` assembles `/api/v1` routes. The example router is included only when explicitly enabled in development/test settings.
5. FastAPI reads the JSON body and constructs `StudentInput` from `app/schemas/learning.py`.
6. If validation succeeds, `validate_student` in `app/api/v1/examples.py` receives a typed Python object and returns `StudentValidationResponse`.
7. FastAPI validates/serializes the response, and middleware adds `X-Request-ID` to the HTTP headers.

The application factory can create separate instances with explicit settings. Tests import that factory rather than Uvicorn's entry point, so they do not start an application using your local `.env` by accident.

## What Pydantic checks

All three fields are required strings. Leading/trailing whitespace is removed before checking that values are nonempty. Names are limited to 100 characters and the admission number to 50 for this example. Unknown fields are forbidden. Names support ordinary Unicode characters and punctuation; this lesson does not establish a school-specific admission-number format.

Pydantic schemas describe input/output. They are not database tables. We will introduce SQLAlchemy table models with persistence.

Try changing `first_name` to spaces, removing `last_name`, using a number as a name, or adding `roles` or `school_id`. These requests return HTTP 422 before the endpoint function runs. [Pydantic fields](https://docs.pydantic.dev/latest/concepts/fields/).

## Understand an error response

For a blank `first_name`, expect the following structure; messages and the generated request ID can vary:

```json
{
  "error": {
    "code": "validation_error",
    "message": "The request did not pass validation",
    "details": [
      {
        "location": ["body", "first_name"],
        "message": "String should have at least 1 character",
        "type": "string_too_short"
      }
    ]
  },
  "request_id": "a-server-generated-UUID"
}
```

`location` identifies the field. `type` provides a stable category for client behavior. The same request ID appears in the response's `X-Request-ID` header. The API generates this ID rather than trusting a caller-provided identifier.

Validation errors omit Pydantic's raw input/context so a rejected value is not echoed into the error payload. Unexpected server errors return a generic HTTP 500 message; logs identify the request and exception type without including request bodies, tokens, or exception text. Expected HTTP errors preserve important headers such as `WWW-Authenticate`.

For troubleshooting, retain the request ID. Never post actual student data or identity tokens in an issue. CORS preflight rejection is handled by the browser middleware and can use its own plain-text response.

## Configuration is data, too

The settings model reads `SMS_` environment variables and the API directory's `.env`, using an absolute path. Environment variables override file values. Settings are validated when the application is constructed; changes require a restart.

| Setting | Meaning |
| --- | --- |
| `SMS_ENVIRONMENT` | `development`, `test`, `staging`, or `production` |
| `SMS_DEBUG` | Debug mode; defaults to false |
| `SMS_ENABLE_LEARNING_ENDPOINTS` | Explicit opt-in for fictional development examples; defaults to false |
| `SMS_CORS_ORIGINS` | JSON list of exact browser origins; defaults to an empty list |

Example CORS value: `["http://localhost:3000","http://127.0.0.1:3000"]`. Wildcards, paths, embedded credentials, malformed ports, and query strings are rejected. Deployed environments require HTTPS for any configured origins and reject debug/learning flags. Staging/production omit public `/docs` and `/openapi.json` routes.

CORS governs which browser origins can read responses. It does not replace authentication or school permissions; those will be implemented in the Python backend before school records are exposed. [FastAPI settings](https://fastapi.tiangolo.com/advanced/settings/).

## Checks and next step

```sh
python3.13 scripts/api.py check
```

Tests cover successful normalization, field rejection, protected-field attempts, safe errors, request IDs, CORS behavior, settings precedence, and deployed-route guards. They use explicit test settings and fictional values.

Before persistence, explain why the example returns 200 rather than 201, why validation runs before the function, why accepted input is not yet a registered student, and why permission checks belong on the backend. Next we will add PostgreSQL, SQLAlchemy, and Alembic, then connect identity and school access to real records.
