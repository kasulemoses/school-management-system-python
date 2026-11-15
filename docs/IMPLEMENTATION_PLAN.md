# Student management system — Python backend implementation plan

Revised: 15 November 2026. Repository: https://github.com/kasulemoses/school-management-system-python

**Architecture decision:** Python is the application backend. FastAPI handles requests, authorization, validation, business rules, database access, integrations, and background processing. Next.js provides the frontend, Neon hosts PostgreSQL, and Firebase Authentication provides identity. This document replaces the earlier SQL Connect design. SQL Connect is not part of the implementation.

The developer already knows Python and wants to understand its use in a web backend. Implement in small, explained steps, with a runnable result and focused verification at each stage. This revision establishes the plan; application scaffolding follows as a separate step.

## 1. Product objective and scope

Build a shared platform for independent primary and secondary schools to manage students, guardians, enrollment, attendance, fees, assessments, and reports. A user can work at several schools while each school's records remain protected.

### Confirmed decisions

- Python owns the application backend through FastAPI.
- Next.js with TypeScript owns the frontend.
- Neon PostgreSQL stores school records; Python connects directly to it.
- Firebase Authentication handles sign-in, email verification, password recovery, and identity tokens.
- School memberships and permissions are stored in PostgreSQL and enforced in Python.
- Python owns the database model and Alembic migrations.
- Custom workflows and jobs remain Python responsibilities.
- Development uses VS Code, a Python virtual environment, version control, and isolated local/staging/production settings.

### First-release scope

Staff access, school settings, academic years/terms/classes, student admission, guardians, enrollment history, daily attendance, manual fee recording and statements, assessments, grading, report cards, and limited guardian/student access. Deliver these in milestones. A staff pilot may start after reliable fees if academic reports are not an immediate operational requirement.

Payment gateways, SMS, timetable generation, boarding, transport, library, payroll, biometrics, offline synchronization, cross-school transfers, subscription billing, custom domains, and advanced analytics are later extensions unless explicitly prioritized.

Country, curriculum, report format, currency, and language remain school settings or kickoff decisions. Do not infer them from the developer's location.

## 2. Architecture and responsibility boundaries

```text
Next.js frontend
  |-- signs the user in through Firebase Authentication
  |-- sends HTTPS API requests with a Firebase ID token
  v
Python backend: FastAPI
  |-- verifies identity using Firebase Admin SDK for Python
  |-- resolves the active application user and school membership
  |-- authorizes the action and validates input
  |-- executes business rules and records audit events
  |-- accesses PostgreSQL using SQLAlchemy + psycopg
  v
Neon PostgreSQL

Python API / Python worker
  |-- private object storage for documents and generated files
  |-- email/SMS/payment providers when required
  |-- background imports, exports, reports, and notifications
```

| Component | Role | Initial choice |
| --- | --- | --- |
| Python | Backend application language | Select a supported interpreter during setup; 3.13 is the proposed conservative baseline |
| FastAPI | HTTP API, routing, dependencies, response contracts | Modular application with versioned REST endpoints |
| Uvicorn | ASGI server that runs the FastAPI application | Development server first; production process settings later |
| Pydantic | Request/response validation and settings | Explicit input and output schemas |
| SQLAlchemy | Database mapping, queries, sessions, transactions | Synchronous implementation initially |
| psycopg | PostgreSQL driver | Compatible psycopg 3 release |
| Alembic | Versioned database changes | Reviewed migrations in source control |
| Neon | Managed PostgreSQL hosting | Staging and production isolated from each other |
| Firebase Auth | Identity and credentials | Client sign-in; Python Admin SDK verifies tokens |
| Next.js | User interface | TypeScript and App Router |
| Private object storage | Photos, documents, reports | Provider selected during the document milestone; API-controlled access |
| Python job worker | Durable long-running work | Introduce a queue when imports/reports/notifications need it |

Choose mutually compatible supported versions, pin direct dependencies, and commit reproducible lockfiles. Audit installed tools before installation; do not assume the newest installed Python is the right interpreter for every dependency.

FastAPI supports modular applications and PostgreSQL integrations; SQLAlchemy is the chosen persistence layer for this project. [Application organization](https://fastapi.tiangolo.com/tutorial/bigger-applications/), [Database integration](https://fastapi.tiangolo.com/tutorial/sql-databases/).

### Backend structure

Start with one Python application organized into domain modules. Requests flow through a router, Pydantic validation, identity/school dependencies, a domain service, SQLAlchemy queries, and a response schema. Small queries can stay in their domain service; add a separate repository layer only when query complexity or reuse justifies it.

Use synchronous route handlers and database sessions at first. Synchronous database/Firebase calls must run through FastAPI's supported synchronous execution path rather than blocking an async event loop. Introduce async code only for a measured need and a complete compatible I/O design.

Open one SQLAlchemy session per request, share it through dependencies, and close it on completion. Domain services own transaction boundaries for business actions; commit once when the action and audit writes succeed, and roll back on failure. Avoid hidden commits inside reusable query helpers.

The browser accesses school data through Python. Next.js may format values and give early form feedback, but Python decides permissions, money calculations, grading, valid transitions, and database changes. Private credentials remain server-side. Generated TypeScript API types can later come from FastAPI's OpenAPI schema.

### Frontend/API connection

During development, run Next.js and FastAPI on separate local ports with an explicit CORS origin allowlist. The initial authenticated dashboard uses Firebase client sign-in and bearer ID tokens. Do not place tokens in URLs or logs, or manually create another long-lived token store.

In production, select compatible frontend and Python hosting near the database. Prefer one public application origin with `/api/v1` routed to Python when practical; otherwise use exact permitted frontend origins. Keep personalized pages and API responses out of shared caches. Protected server rendering, if introduced later, requires a deliberate server authentication flow.

## 3. Repository organization

Use a single repository for frontend, Python backend, migrations, tests, and documentation:

```text
school-management-system-python/
  apps/
    api/
      app/
        main.py                 # FastAPI app and router registration
        api/v1/                 # Versioned endpoint routing
        core/                   # Settings, identity checks, errors, logging
        db/                     # Engine, session dependency, model metadata
        modules/
          access/               # Users, memberships, invitations
          schools/              # School profiles and settings
          academics/            # Years, terms, classes, teaching assignments
          students/             # Profiles, guardians, enrollment
          attendance/
          finance/
          assessments/
        jobs/                   # Python workers as durable jobs are introduced
      migrations/
        versions/
      tests/
        unit/
        integration/
      pyproject.toml
      uv.lock
      alembic.ini
      .env.example
    web/
      src/app/                  # Next.js routes and layouts
      src/components/
      src/features/
      src/lib/                  # Firebase client and Python API client
      .env.example
      package.json
  tests/e2e/                    # Browser workflows
  tests/fixtures/               # Fictional seed inputs
  scripts/                      # Setup, seeds, and development helpers
  docs/
    IMPLEMENTATION_PLAN.md
    BACKLOG.md
    PYTHON_BACKEND_LEARNING_GUIDE.md
    PERMISSIONS.md
    DATA_MODEL.md
    DEVELOPMENT.md
    DEPLOYMENT.md
    OPERATIONS.md
    decisions/
  .vscode/                      # Shared editor recommendations and debug tasks
  .github/workflows/
  compose.yaml                  # Proposed local PostgreSQL service
  .gitignore
  .python-version
  package.json
  pnpm-workspace.yaml
  pnpm-lock.yaml
  README.md
```

This is the target structure; application files will be created during setup. Add each domain directory when its feature starts rather than filling the repository with unused stubs. Inside a domain, use models, schemas, router, and service files where relevant.

Use uv for the proposed Python dependency/environment workflow and pnpm for the frontend workspace. A `.venv` isolates Python dependencies; it is not the database or the backend server. Lockfiles record resolved versions. Explain each tool and command when introduced. VS Code should use the project's virtual-environment interpreter and have explicit launch tasks for Python and Next.js.

Add a README, environment examples, setup instructions, issue/PR templates, and basic CI. Use short feature branches after the initial repository commit. Each change explains user behavior, permissions, migrations, and validation. Choose a license once ownership/distribution is settled.

## 4. Environments and local setup

| Environment | Purpose | Services |
| --- | --- | --- |
| Local | Development and learning using fictional records | Python API, Next.js, PostgreSQL, Firebase Auth emulator |
| Staging | Verify cloud identity/database behavior and demonstrate features | Separate hosting, Firebase project, Neon database, private storage |
| Production | Real school operations | Isolated production configuration, credentials, records, backups |

Setup sequence: inspect available tools → choose the supported Python version → create the isolated environment → install locked dependencies → run the first FastAPI endpoint → inspect `/docs` → add PostgreSQL → create the first migration → add identity verification → connect Next.js. Start one new moving part at a time.

Use Docker Compose for local PostgreSQL if Docker is available and the user wants it; otherwise use a supported local PostgreSQL installation. Do not substitute SQLite for tests involving PostgreSQL constraints, money, relationships, or concurrency. Use the Auth emulator for development and real Firebase identity tests in staging.

Document backend-only and full-stack startup separately. A learner should be able to run and explore Python endpoints without first running the frontend. Include Windows equivalents if another development machine is introduced.

Backend settings include runtime mode, database URLs, allowed origins, Firebase project ID, and storage/integration configuration. Separate privileged secrets from public Firebase web configuration. Validate required production settings at startup; emulator bypasses/debug identity settings must never enable in production.

Keep `.env` files, service-account keys, real student data, virtual environments, local database contents, logs, and private exports out of Git. Prefer managed deployment identities and secret storage for production credentials.

Neon application requests use an appropriate pooled connection; migrations and administrative commands use a direct connection. Bound SQLAlchemy pools across all API/worker processes and configure TLS. Verify transaction-pooling compatibility and avoid reliance on session-level state. [Neon connection guidance](https://neon.com/docs/connect/connection-pooling).

## 5. Authentication, school membership, and authorization

### Identity flow

1. Next.js signs the user in through Firebase Authentication.
2. The Firebase client SDK obtains an ID token and sends it in `Authorization: Bearer ...` on HTTPS requests to Python.
3. A FastAPI dependency uses the Firebase Admin SDK for Python to verify signature, project, expiry, and revocation/account status according to the configured policy. Start with explicit revocation checks; measure upstream verification latency before optimizing.
4. Python maps the verified Firebase UID to an active application User. Email is a contact attribute, not the stable identity key.
5. For a school route, Python verifies active school status, membership, role, and relevant teaching/guardian/student relationships.
6. Python queries and changes only the authorized school's records, returning an explicitly allowed response shape.

Firebase ID-token verification supports Python. Ordinary token verification does not automatically check revocation; implement that policy explicitly. The database remains authoritative for current school access, so suspension does not wait for token refresh. [Firebase verification](https://firebase.google.com/docs/auth/admin/verify-id-tokens).

Use one identity account per person, memberships across schools, and several fixed initial roles per membership. Students and guardians can have school records without login accounts. Account registration does not automatically grant school membership. Creating a User profile from a verified identity never accepts caller-supplied privileges.

School creation and the first administrator use a controlled Python command/service. Staff invitations are single-use, expire, and bind permitted roles to the intended verified identity. Prevent accidental removal of the last active administrator. Guardian account access requires a verified relationship, not just matching contact details.

School, user, and membership suspension are separate states. Define permitted recovery/export actions. On sign-out or school switching, clear sensitive frontend query state and discard late responses from the prior context; cache keys include actor and school. Firebase client sign-out and server-side revocation are different actions and must be tested accordingly.

### Initial role matrix

These are proposed defaults; finalize `docs/PERMISSIONS.md` before each module ships. Combined roles grant the union of explicitly allowed actions within that school. School-wide administrative access remains auditable.

| Role | Student/guardian records | Attendance | Fees | Results | Access administration |
| --- | --- | --- | --- | --- | --- |
| School administrator | Manage ordinary school records | Manage | Manage | Configure, approve, publish | Manage permitted roles in own school |
| Registrar | Manage admissions and enrollment | View summaries | View clearance/balance only if permitted | View published school reports | None |
| Teacher | Minimum needed for assigned classes | Mark assigned classes | None | Enter assigned marks; publication requires approval role | None |
| Bursar/accountant | Minimum identity/enrollment needed for billing | None by default | Issue invoices, record payments, reconcile | None | None |
| Guardian | Approved linked children only | View allowed summaries | View allowed invoices/receipts | Published reports only | None |
| Student | Own permitted profile fields | View own allowed summary | View own balance if enabled | Own published reports only | None |
| Platform operator | School lifecycle and platform configuration | No default student-data browsing | No default finance browsing | No default results browsing | Platform operations only |

Platform support access to school records requires an explicit, scoped, expiring grant and an audit trail. Emergency operational database access is separate from ordinary product roles. No role is granted merely because a browser sends its name.

### Python authorization contract

Every endpoint, background job, and integration must define the actor, required roles, school scope, allowed fields, related-record ownership, valid state transitions, and audit behavior. Reusable dependencies resolve the current user and authorized school context; domain services enforce action-specific permissions.

All list/detail/search/count/export queries are explicitly school scoped. Check object-level ownership after resolving identifiers. Do not authorize an operation merely because a caller supplied an authorized school ID alongside another school's student ID. Validate nested relationships and exclude protected fields such as school ownership, role grants, and posted finance fields from ordinary update schemas.

Background jobs persist the requester and school and recheck access before sensitive execution/download. Platform operators manage the platform; student-data support access requires an explicit, scoped, expiring grant and audit history. Private files follow the same record permissions.

Use database constraints where feasible and application authorization everywhere. PostgreSQL row-level security can be evaluated as an additional layer only after designing transaction-scoped context compatible with pooling and testing it; do not claim it is enabled before implementation.

## 6. Data model and durable business rules

Use school ownership on every school-specific entity. Keep global identity separate from school-owned personal records to avoid accidental disclosure between schools. Validate relationships within the same school; add database uniqueness/foreign-key constraints wherever supported. Any supplementary constraint outside generated Alembic-managed schema must have a reviewed, repeatable migration procedure and compatibility test.

| Area | Main records | Required behavior |
| --- | --- | --- |
| Platform/access | User, School, Membership, MembershipRole, Invitation, SupportGrant, AuditEvent | UID uniqueness; scoped roles; invitation expiry; explicit support access |
| Academic structure | AcademicYear, Term, ClassLevel, ClassGroup, Subject, TeacherAssignment | School-specific naming, dates, and subjects; class groups belong to an academic year |
| Registry | Student, Guardian, StudentGuardian, Enrollment, ClassPlacement, StudentDocument | School-unique admission number; multiple guardians; historical placement; optional account links |
| Attendance | AttendanceSession, AttendanceRecord, AttendanceCorrection | Unique student/session; consistent enrolled roster; correction history |
| Finance | FeeScheduleVersion, Invoice, InvoiceLine, Payment, PaymentAllocation, Adjustment, Receipt | Exact amounts, immutable posted records, allocation/reversal history |
| Assessment | Assessment, Component, SubjectOffering, GradeScaleVersion, Mark, ResultPublication, ReportSnapshot | Valid marks/weights; approval; versioned grading; reproducible publication |
| Jobs | ImportJob, ExportJob, NotificationJob, IdempotencyRecord | School context, retries, duplicate protection, progress and failure states |

### Shared rules

- Use stable internal identifiers; admission numbers are school-scoped business identifiers.
- All meaningful changes record actor and server time. Store instants in UTC and interpret school dates using the configured school timezone.
- School ownership is immutable through ordinary update operations.
- Archive/deactivate referenced records rather than deleting enrollment, financial, or published academic history.
- Use version/revision checks for concurrent editing where lost changes matter.
- Paginate lists and bound filters/exports; index school plus frequent access paths.
- Avoid a generic JSON field for core relationships and permissions. Use structured records for things that need validation, joins, or reports.

### Registry and enrollment

Admission captures the minimum required identity, admission date/number, status, guardian contacts, and academic placement. Sensitive extra fields require an operational reason and restricted access.

Enrollment represents a student's participation in a school academic year. ClassPlacement preserves moves between groups/streams with effective dates. Proposed policy: one active enrollment per student per academic year, with placement history instead of overwriting the class. Confirm term-specific exceptions before schema finalization. Promotion creates new year enrollment; transfers preserve the original school's history.

Guardian contact records are school-owned. A verified account can link to guardian records in several schools, but matching names, phone numbers, or email addresses do not automatically merge private school records. Creating a contact does not grant portal access.

### Attendance

Start with daily attendance using the school's date and configured statuses. Period attendance is an extension. Only an assigned teacher or authorized administrator can mark the roster. Corrections include actor, reason, and time. Class moves and withdrawals must not rewrite the historical attendance roster. Bulk writes must report clear atomicity or partial-failure behavior and support safe retry.

### Finance

Start with manual payment recording. Define currency and amount scale; use exact fixed-scale values or integer minor units with end-to-end precision checks. Never calculate balances using floating-point arithmetic. Store invoice line snapshots so later fee changes do not alter issued invoices.

Invoice states: draft → issued → partially paid/paid, with controlled void/credit paths. Payment and allocation are distinct: support partial payment, several invoices per payment, and explicit unapplied credit. Derive balances from posted charges, allocations, and adjustments. Posted records are corrected through traceable reversals, not silent edits or deletion.

Post related financial records and audit entries in one transaction. Enforce idempotency keys and unique external references. A transaction alone is not proof against concurrent over-allocation: prototype conditional updates, constraints, or another supported concurrency strategy and test simultaneous requests. Retrying a function must not create another payment or receipt.

Gateway integration follows manual-finance acceptance. It requires signature verification, reconciliation, duplicate/out-of-order webhook handling, currency/amount comparison against stored orders, and a clear pending/failed/refunded model. Browser redirects never prove settlement.

### Assessments and report cards

Make subjects, maximum marks, weights, grading bands, rounding rules, missing marks, and remarks configurable per school. Version rules by academic period. Workflow: draft marks → submitted → approved → published. Teachers can enter only assigned marks; approval/publication require explicit permission.

Published results use a stored snapshot or an equivalently reproducible versioned representation. Later changes produce a controlled revised publication rather than silently rewriting an old report. Guardian/student queries can only retrieve allowed published results. Report downloads use private storage and school-authorized access.

## 7. API and database conventions

Version endpoints under `/api/v1`. Proposed routes include:

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Process liveness, without exposing private configuration |
| `GET /ready` | Dependency readiness suitable for deployment monitoring |
| `GET /api/v1/me` | Current application user and permitted profile fields |
| `GET /api/v1/me/schools` | Authorized school memberships |
| `GET /api/v1/schools/{school_id}/students` | Paginated, school-scoped student list |
| `POST /api/v1/schools/{school_id}/students` | Validated, authorized student creation |
| `GET /api/v1/schools/{school_id}/students/{student_id}` | Student detail with object-level access |
| `POST /api/v1/schools/{school_id}/enrollments` | Enrollment with consistency checks |

These are contracts to implement, not endpoints already available. Use dedicated action endpoints for invitation acceptance, publication, payment posting, and reversal rather than broad arbitrary updates.

Use separate Pydantic create/update/read schemas and SQLAlchemy table models. Reject protected or unexpected write fields. Return consistent errors and pagination metadata; use request IDs for troubleshooting. Treat 401 as missing/invalid identity, 403 as forbidden action, 404 as an unavailable record without leaking private existence, 409 as a conflict, and validation failures according to the API contract.

Use SQLAlchemy bound parameters and model expressions. Keep finance/grading calculations in domain services. Database constraints provide a final guard against duplicates and invalid relationships. Test simultaneous requests; a preliminary uniqueness lookup alone cannot prevent a race.

Alembic owns versioned schema changes. Review generated migrations before applying them, test them against PostgreSQL, and run migrations once per release. Avoid production table creation through `create_all` at API startup. Use additive changes → backfill → deploy compatible code → retire old fields later. Code rollback and database restoration are distinct procedures.

The API owns transactions: write related domain records and audit events together. Use revision checks, database constraints, row locks, or conditional writes where concurrency requires them. Introduce idempotency keys for retryable actions. Durable background work uses a Python worker and queue; do not rely on request-process background tasks for critical jobs that must survive restarts.

## 8. User interface and navigation

Build one consistent application shell with role-sensitive navigation and a clearly visible current school. The initial sidebar includes Dashboard, Students, Classes, Attendance, Fees, Assessments, Reports, Staff, and Settings as those modules become available. Hide unfinished modules or label controlled previews deliberately.

Core screens: login/recovery, school selection, school settings, staff invitations, academic setup, student list/profile/admission, guardian links, enrollment history, attendance roster, fee account/receipts, marks entry, publication review, and reports. Platform operator screens are separately restricted.

Design for ordinary school office work: keyboard-accessible forms, readable tables, clear search/filter controls, mobile layouts, explicit validation, loading/empty/error states, and recovery after a failed request. Confirm high-impact actions such as financial reversal or result publication with a clear consequence and a reason field where appropriate.

Support useful list pagination and bulk actions with preview and results. Avoid collecting all students into the browser. Use school settings for dates, currency, branding, and terminology. Start with one agreed language; structure copy for later localization if needed.

## 9. Milestones and acceptance gates

Calendar estimates follow the first technical proof and confirmation of development capacity. Teach the Python request lifecycle before adding frontend integration.

| Milestone | Deliverables | Exit criteria |
| --- | --- | --- |
| M0: Python web foundation | Environment, FastAPI app, Uvicorn, health endpoint, request/response schemas, `/docs`, basic endpoint checks | Developer can run the API, send a request, explain validation, and trace its response |
| M1: Persistence and school isolation | SQLAlchemy, PostgreSQL, Alembic, users, schools, memberships, Firebase verification, scoped queries | Data survives restarts; migrations recreate schema; school A cannot access B; suspended membership rejected |
| M2: Student registration and enrollment | Years/terms/classes, invitations, students, guardians, enrollment history, Next.js integration, staging | Administrator completes the first full workflow; foreign IDs, duplicates, and partial writes are handled safely |
| M3: Attendance | Teaching assignments, daily rosters, marking, corrections, summaries | Staff manage only assigned rosters; duplicate and historical-placement cases tested |
| M4: Fees | Fee versions, invoices, manual payments, allocations, receipts, reversals, statements | Exact balances reconcile; retries/concurrent allocations are safe; posted history is protected |
| M5: Academics | Subjects, assessments, grade versions, mark entry, approval, publication, reports | Approved results reproduce their rules; unpublished data stays private; revisions are audited |
| M6: Portals and pilot | Verified guardian/student access, imports/exports, chosen notifications, operational readiness | Two-school pilot, measured performance, access review, and successful recovery drill |

For every milestone: explain the relevant Python files/request flow, implement one meaningful workflow, run focused checks, demonstrate it in staging when relevant, and update documentation. Do not call a feature complete when it works only with mock data.

### First complete product demonstration

An authorized administrator signs in, selects a school, creates an academic year/term/class, registers a student, links guardian contacts, enrolls the student, edits an allowed detail, and views audit/history. Another school's administrator is denied the same record identifiers. Suspending the first user's membership rejects subsequent API calls.

The first learning checkpoint is smaller: a running Python endpoint and an explanation of every line. The initial backlog builds from that checkpoint to the full demonstration.

## 10. Verification strategy

Use pytest for Python tests, an HTTP test client for FastAPI, and PostgreSQL-backed integration tests for real persistence/constraints. Keep tests isolated and use fictional data. Do not run migrations or cleanup against a production database during tests.

Permission fixtures include schools A/B, a user in both with different roles, assigned/unassigned teachers, a bursar, linked/unlinked guardians, and suspended memberships. Invoke the Python HTTP API as ordinary authenticated users, independently of browser guards. Mock identity at a narrow test boundary for deterministic cases; test real Firebase verification in staging and compatible emulator cases locally.

Cover list/detail/create/update, searches/counts, guessed IDs, cross-school foreign relationships, role escalation, school ownership changes, stale memberships, unpublished results, documents, and exports. Every new protected endpoint requires meaningful access coverage.

Domain/concurrency tests cover unique admission numbers, enrollment constraints/history, duplicate attendance, exact amounts, repeated payments, simultaneous allocations, edit version conflicts, weighted/missing marks, publication history, and transaction rollback. Add migration checks from an empty PostgreSQL database and representative upgrade paths.

Browser tests cover login, school switching/cache clearing, enrollment, attendance, payment recording, and report access as features ship. Check keyboard use, helpful validation, and practical mobile layouts. Staging verifies actual Neon connections, Firebase credential behavior, file access, deployed Python workers, and release compatibility.

Before load testing, agree school/student counts, busiest workflows, concurrency, and report size. Proposed targets: p95 ordinary API list/detail operations under 1 second and p95 routine page usability under 3 seconds on an agreed pilot connection. Measure these targets, including identity-verification overhead; they are not platform guarantees. Large reports/exports run as queued jobs with progress.

## 11. Imports, files, jobs, and auditing

Imports use a downloadable template, mapping, validation preview, row errors, duplicate policy, idempotent execution, and a final summary. Import history stores actor, school, source metadata, status, and counts. Avoid silently replacing good data with blanks. Export authorization is checked both when creating the job and when retrieving the result.

Private file paths include school ownership and random object identifiers. Authorize upload/download through Python API endpoints that check current database memberships. Use short-lived access, size/type limits, server validation, and scanning before exposing untrusted uploads. Deleting or suspending access cannot retract an already downloaded file; expiry bounds outstanding download links. Do not treat an object path or an unguessable URL as permission.

Background jobs store school, requester, purpose, status, attempt count, and idempotency key. Retry safe operations, record failed jobs, and provide an operator retry path. Separate database commits from external delivery through a transactional job/outbox record where needed; email delivery cannot be part of a PostgreSQL atomic commit. Never label a notification delivered solely because it was queued.

Domain audit events are application records protected from ordinary edits. Record actor, school, operation, target, server timestamp, request/job identifier, and an appropriate change summary. Minimize sensitive copied values. Log access grants, membership changes, enrollment changes, attendance corrections, issued/posted financial actions, result publication, and exports. Infrastructure logs complement these records but do not replace them.

## 12. CI, deployment, monitoring, and recovery

### Pull request checks

Install from lockfiles, run Python formatting/static checks and focused tests, validate migrations against an isolated PostgreSQL service, type-check/build the frontend, and run relevant browser workflows. Check OpenAPI/type generation when contracts change. Do not give untrusted pull requests production secrets or deployment access.

### Deployment

Deploy Next.js and the Python API as separate services, with a separate Python worker when durable jobs are introduced. Select providers based on region, cost, persistent-process/queue requirements, and database proximity. A PostgreSQL-compatible hosting change should not require rewriting domain services.

Release flow: review migration impact → test on staging → apply compatible migrations once → deploy API/worker → deploy frontend consumers → verify ordinary-user workflows → record release commit → monitor. Keep the previous compatible application build. Destructive schema changes and backfills require explicit rollout/recovery plans.

Configure TLS, exact allowed origins, managed secrets, request limits, identity/invitation abuse controls, and least-privilege runtime/database access. Log request IDs and safe error context, never tokens or private student payloads. Monitor API latency/errors, authorization failures, database connections, worker jobs, storage errors, and spending.

### Recovery and retention

Before real data, select database backup/PITR settings, private-file recovery policy, and achievable recovery objectives. Proposed discussion targets are recovery point within 1 hour and recovery within 4 hours; confirm configuration and cost before promising these to schools. Restore database and referenced files in an isolated drill.

Define retention for registry, financial, audit, exported, and deleted-file data with the schools. Document school offboarding/export, account removal, and approved deletion. Confirm operating countries before specifying jurisdiction-dependent obligations.

## 13. Costs and production choices

Budget for Neon PostgreSQL, Python API hosting, optional Python workers/queue, Next.js hosting, private storage/egress, backups, logs, and selected email/SMS/payment services. Check Firebase Auth provider and MFA requirements before activation. Choose production capacity from expected usage and recovery requirements rather than treating a free tier as the production specification.

Kickoff records monthly budget, regions, school/student counts, peak users, retention, availability, and notification volume. Compare minimal staging with a production configuration that meets recovery needs. Spending alerts notify operators; they do not necessarily cap expenditure.

## 14. Step-by-step implementation and learning workflow

1. Add this revised plan, the Python backlog, README, and learning guide to the repository.
2. Open the repository in VS Code and inspect installed tools; choose the compatible Python interpreter.
3. Explain and create the isolated Python environment and dependency configuration.
4. Build a minimal FastAPI application, run it through Uvicorn, inspect `/docs`, and send a request.
5. Add one Pydantic request/response example and show how invalid input is rejected.
6. Introduce local PostgreSQL, SQLAlchemy models/session dependency, and the first Alembic migration.
7. Add Firebase identity verification and explicit school-membership dependencies.
8. Test two-school isolation through Python HTTP endpoints before expanding domain features.
9. Build student/guardian/enrollment services with transactions and audit events.
10. Scaffold/connect Next.js and trace a real frontend request through Python to PostgreSQL.
11. Seed fictional schools, demonstrate the workflow, and deploy staging when account access/configuration is available.

For each step: explain purpose → show the small change → run it → inspect the result → discuss how it fits the request lifecycle. The developer knows Python; focus explanations on web frameworks, HTTP, dependency injection, validation boundaries, persistence, transactions, identity, and deployment.

Local development can start before production cloud accounts exist. Do not silently provision paid resources. This plan revision does not scaffold application code or deploy a service.

## 15. Kickoff decisions to capture

| Decision | Needed before | Proposed starting position |
| --- | --- | --- |
| Repository URL, owner, and access | First shared commit | Repository supplied; verify access before publishing |
| Operating countries, curricula, terminology | Academic schema and school settings | Configurable; no assumed country |
| School count, size, campuses, and shared staff | Sizing and final access model | Shared platform; memberships can span schools; campus model to confirm |
| First operational priority | Milestone refinement | Registry → attendance → fees → assessments |
| Academic years/terms and grading examples | Academic setup and assessment implementation | School-specific, versioned rules |
| Admission numbering and current spreadsheets | Registration/import implementation | School-unique numbers and validated import |
| Currency, fee rules, receipts, and refunds | Finance implementation | One currency per school initially; manual recording first |
| Guardian verification and student account policy | Portal implementation | Explicit verified relationships; optional student logins |
| Hosting region, budget, backups, and recovery | Cloud provisioning and production pilot | Choose separate Python/Next.js hosts near Neon; measure costs before production |
| Email/SMS and payment providers | Integration implementation | Choose after core workflows work |
| Languages, accessibility, and offline needs | Interface/integration scope | Accessible responsive interface; offline sync as a separate feature |

## 16. Production completion criteria

Two pilot schools can run the agreed workflows; Python API tests demonstrate school isolation; money/grading rules pass integrity checks; every backend path enforces permissions; files remain private; deployment/migrations are repeatable; monitoring is active; recovery is demonstrated; and school administrators have operating instructions. Track remaining noncritical issues with owners and workarounds.

## Technical references

- [FastAPI first steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [FastAPI modular applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [FastAPI relational database integration](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Alembic migrations](https://alembic.sqlalchemy.org/en/latest/)
- [Firebase Admin ID-token verification](https://firebase.google.com/docs/auth/admin/verify-id-tokens)
- [Neon SQLAlchemy integration](https://neon.com/docs/guides/sqlalchemy)
- [Neon connection pooling](https://neon.com/docs/connect/connection-pooling)
