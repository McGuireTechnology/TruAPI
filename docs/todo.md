# TruAPI TODOs

This file captures prioritized engineering tasks discovered from scanning the `truapi/` package.

## Platform & App
- Configuration: Externalize `APP_*` envs and document `.env` loading. Add example `.env` and secure defaults.
- Observability: Add request logging, structured logs, and error telemetry hooks.
- CI/CD: Add GitHub Actions for lint, type-check, tests, and docs build. Cache Poetry.
- Docs: Link MkDocs site and publish instructions. Add API usage examples.

## REST API
- Router composition: Confirm `exception_container(app)` coverage; document handlers and expected formats.
- Validation: Extend Pydantic models with constraints (username length, display name limits).
- Pagination & filtering: Add pagination for `/users` list; document query params.
- Error shapes: Standardize error response schema with codes.
- OpenAPI: Ensure tags, summaries, and examples for all endpoints.

## Domain & Use Cases
- User entity: Add invariants (non-empty username/email), normalization (lowercasing email), and basic validation.
- Use cases: Ensure idempotency rules for create/update; extend tests beyond happy-path.
- Exceptions: Review `UserNotFoundError` usage; add domain-level errors for conflicts.

## Repositories & Storage
- SQLAlchemy wiring: Provide AsyncSession factory and engine config; add migrations.
- Transactions: Ensure atomic operations for multi-step use cases.
- In-memory repo: Keep for tests; ensure parity with SQLAlchemy implementation.
- Filters: Expand `_apply_filters` to support partial matches and case-insensitivity where appropriate.

## Testing
- Coverage: Consolidate tests under `tests/` and raise coverage thresholds.
- Async tests: Add tests for SQLAlchemy repo with an ephemeral DB (SQLite in-memory or test container).
- API tests: Add FastAPI `TestClient` integration tests for all endpoints.

## Security & Auth
- Authentication: Introduce minimal authn (API key/JWT) and dependency wiring.
- Authorization: Define roles/permissions and protect routes where needed.
- Input sanitization: Harden inputs and enforce email format beyond EmailStr if needed.

## Performance & Reliability
- Startup/shutdown: Add lifespan handlers to initialize/recycle resources.
- Timeouts/retries: Add DB and external call timeouts; basic retry policy.
- Caching: Consider simple read-through cache for frequent reads.

## Backlog (Future)
- Rate limiting & throttling
- Multi-tenant boundaries and context propagation
- Audit logs for user mutations
- Data export/import endpoints

---

### Quick Wins (Suggested Next Steps)
1. Add GitHub Actions workflow: lint (ruff), format (black check), mypy, pytest.
2. Implement AsyncSession factory and wire `repo_dep("user")` to SQLAlchemy repo by default.
3. Add pagination to `/users` list and update docs.
4. Strengthen `User` invariants and update tests accordingly.
