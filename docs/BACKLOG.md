# Initial Python backend backlog

Revised: 15 November 2026. Architecture: Next.js → Python/FastAPI → Neon PostgreSQL, with Firebase Authentication. These are planning issue IDs, not existing GitHub issues. Complete the learning checkpoints before expanding the application. No application tasks below are marked complete merely because the plan exists.

## Checkpoint 1 implementation status

- SETUP-01: Implemented with Python 3.13, isolated tooling/application environments, locked dependencies, VS Code configuration, and setup instructions.
- API-01: Implemented with FastAPI/Uvicorn, `GET /health`, interactive documentation, and HTTP checks.
- API-02 onward: Upcoming. The health response is the first response-model example; full request validation, configuration, persistence, and identity checks follow.

Follow [Development](DEVELOPMENT.md) to run the checkpoint and understand each part.

## SETUP-01 — Establish the Python project and VS Code workspace

**Deliver:** Supported interpreter selection, isolated virtual environment, pyproject and lockfile, clear backend directory structure, environment examples, VS Code interpreter/debug settings, and README setup instructions.

**Acceptance:** A fresh checkout can install the locked Python dependencies. The developer can explain the interpreter, virtual environment, package manager, and application directory. Secrets/local state are ignored. Versions are chosen for dependency compatibility, not just because they are installed.

**Depends on:** Architecture decision. **Learning:** How a Python web project is organized.

## API-01 — Run the first FastAPI endpoint

**Deliver:** FastAPI app, Uvicorn startup, a safe health endpoint, interactive `/docs`, and a focused HTTP check.

**Acceptance:** Developer can start/stop the server, send a GET request, explain the route decorator and JSON response, and distinguish application code from the ASGI server. Startup uses documented local commands and no production resources.

**Depends on:** SETUP-01. **Learning:** Request → router → Python function → HTTP response.

## API-02 — Define validation, settings, and API contracts

**Deliver:** Pydantic input/output schemas, versioned router organization, consistent errors, configuration validation, explicit local CORS settings, and request IDs.

**Acceptance:** Invalid data fails before domain writes; protected/unknown fields are rejected; output schemas omit private/internal values. Production cannot enable development identity shortcuts. Developer can compare path/query/body/header inputs.

**Depends on:** API-01. **Learning:** Data contracts, HTTP semantics, dependencies, configuration.

## DB-01 — Add PostgreSQL, SQLAlchemy, and Alembic

**Deliver:** Isolated local PostgreSQL setup, SQLAlchemy engine/session dependency, initial User/School/Membership schema, reviewed first migration, and rollback behavior.

**Acceptance:** Schema recreates from migrations; records survive API restarts; sessions close correctly; failed multi-write work rolls back. Constraints reject duplicates and invalid references. Tests use PostgreSQL, never the production database.

**Depends on:** API-02. **Learning:** Database driver vs ORM vs session vs transaction vs migration.

## AUTH-01 — Verify Firebase identities in Python

**Deliver:** Firebase Admin SDK integration, bearer-token dependency, Firebase UID mapping, inactive-account handling, emulator configuration, and staging-verification checklist.

**Acceptance:** Missing/invalid/expired/wrong-project credentials fail. Revocation checking is deliberate and tested. Account registration alone grants no school access. Caller-supplied roles/UIDs cannot override the verified actor. Tokens and privileged keys never enter logs or frontend bundles.

**Depends on:** DB-01. **Learning:** Authentication and the boundary between Firebase and Python.

## ACCESS-01 — Implement school authorization and prove isolation

**Deliver:** Active membership/role dependencies, school-scoped query conventions, restricted platform roles, and two-school API integration tests.

**Acceptance:** Cross-school list/detail/write/search/count requests fail or return only authorized data. A foreign record ID cannot be paired with the caller's school ID. A person in two schools has correct separate permissions. Membership suspension affects the next protected request. Tests call Python endpoints as ordinary identities.

**Depends on:** AUTH-01. **Learning:** Authorization, object access, and multi-school boundaries.

## SCHOOL-01 — Provision schools and invite staff

**Deliver:** Controlled bootstrap command/service, school settings, school administrator assignment, invitations/expiry/acceptance, scoped role administration, and transactional audit events.

**Acceptance:** Retries cannot duplicate provisioning or membership. Invitations bind to the intended verified identity. Ordinary staff cannot grant platform privileges or cross-school access. Last-administrator protection and recovery are defined. Sensitive changes are audited.

**Depends on:** ACCESS-01. **Learning:** Domain services, state transitions, idempotency, audit records.

## ACADEMIC-01 — Define academic periods and class groups

**Deliver:** Academic years, terms, class levels, and year-specific class groups/streams with models, migrations, services, schemas, and endpoints.

**Acceptance:** Server validates dates and same-school relationships. Names are configurable. Used records cannot be destructively removed. Each school's structure is independent.

**Depends on:** SCHOOL-01. **Learning:** Relational modeling and migrations as features evolve.

## STUDENT-01 — Implement students and guardians

**Deliver:** Student registration/list/detail/update/archive, school-unique admission numbers, guardian contacts, explicit relationships/access rights, pagination, and audit events.

**Acceptance:** Student accounts are optional. Concurrent duplicate admission numbers are rejected by constraints. Cross-school guardian links fail. Matching contact details do not auto-merge private records. Protected ownership/role fields cannot be changed. Guardian contact creation alone does not grant portal access.

**Depends on:** ACCESS-01, ACADEMIC-01. **Learning:** Validated CRUD, relationships, response schemas, pagination.

## ENROLL-01 — Implement enrollment and placement history

**Deliver:** Academic-year enrollment, dated class placement, combined admission/enrollment service, transaction boundaries, and conflict handling.

**Acceptance:** Duplicate active enrollment follows the agreed policy and is prevented safely under concurrency. Class changes preserve history. Failed combined workflows do not leave unintended partial writes. Domain and audit changes commit together. Retrying requests has a defined outcome.

**Depends on:** STUDENT-01, ACADEMIC-01. **Learning:** Atomic business actions and database concurrency.

## WEB-01 — Connect Next.js to the Python API

**Deliver:** Next.js/TypeScript app shell, Firebase client sign-in, typed API client, authorized school selection, class/student/guardian/enrollment screens, and browser workflow checks.

**Acceptance:** School records flow through Python endpoints. Auth headers are attached safely. School switching clears/cancels stale data. Direct API authorization still works without UI guards. The developer can trace a submitted form through Python validation/services to PostgreSQL and back.

**Depends on:** AUTH-01, ENROLL-01. **Learning:** Frontend/backend integration and API contracts.

## RELEASE-01 — Automate checks and demonstrate staging

**Deliver:** Repeatable fictional fixtures, CI for Python/PostgreSQL/frontend, reviewed migration/deployment process, separate staging resources, monitoring basics, and setup notes.

**Acceptance:** Fresh checkout passes setup/checks; ordinary users complete the two-school demonstration and fail unauthorized operations. Cloud credentials are isolated. Migrations run once per release. Deployment identifies the commit and records remaining gaps. Staging access and account provisioning are documented.

**Depends on:** WEB-01 and all relevant backend tasks. **Learning:** Production processes, reproducibility, and release validation.

## Later milestone groups

- Attendance: assigned rosters, daily marking, correction history, duplicate/concurrency tests.
- Finance: exact amounts, invoice snapshots, transactional manual payments/allocations, idempotency, receipts, reversals, reconciliation; gateways afterward.
- Assessment: versioned grade rules, mark limits, approval/publication, reproducible reports, controlled corrections.
- Portals/pilot: verified guardian/student access, Python imports/exports/report jobs, selected integrations, load testing, and recovery drill.

## Shared completion requirements

Explain purpose and request flow, make a small reviewable change, run relevant checks, demonstrate actual behavior, and update documentation. Protected features include Python authorization and server validation; related writes use explicit transactions; important changes have an audit trail. Do not replace PostgreSQL behavior tests with SQLite or treat browser hiding as access control.
