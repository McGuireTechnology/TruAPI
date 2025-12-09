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

### Resource-Level ACLs & DACLs
- Model: Define `ACL` (allow/deny entries) and `DACL` (default ACL) domain models with principals (user, group), actions, and resource identifiers.
- Storage: Create repositories for ACL/DACL persistence (SQLAlchemy tables: `acls`, `acl_entries`, `dacls`).
- Evaluation: Implement policy engine with ordered evaluation: explicit deny > explicit allow > DACL > fallback.
- Inheritance: Support hierarchical resources (e.g., parent/child) with DACL inheritance rules and overrides.
- API: CRUD endpoints for managing resource ACLs and DACLs; validation of principals and actions.
- Caching: Add short-lived cache for evaluated permissions per principal/resource to reduce DB hits.
- Auditing: Log ACL changes and evaluation decisions for traceability.

### Endpoint-Level ACLs
- Decorators: Provide FastAPI dependency/decorator to declare required actions/permissions on endpoints.
- Mapping: Maintain mapping between endpoint identifiers (route+method) and required permissions.
- Middleware: Add pre-request check that evaluates principal permissions versus endpoint requirement.
- Overrides: Support endpoint-specific overrides and feature flags for gradual rollout.

### API Keys
- Models: Define API Key entity (id, hashed key, scopes, owner, status, expiry).
- Generation: Implement secure key generation and hashing (e.g., HMAC or SHA-256) with prefix for identification.
- Scopes: Integrate key scopes with ACL engine to restrict actions/resources.
- Rotation: Add rotation & revocation flows; store last-used timestamps.
- Rate limiting: Optional per-key quotas and throttling hooks.
- Endpoints: Issue, list, revoke keys; display partial key once on creation.

### Groups
- Models: Group entity and membership relationships (user↔group, group↔group for nesting if needed).
- Repositories: CRUD for groups and memberships; uniqueness constraints.
- Integration: Use groups as principals in ACL/DACL evaluation.
- Endpoints: Manage groups and memberships; pagination and search.
- Sync: Optional provider sync (e.g., external IdP groups) with reconciliation.

### MFA (Multi-Factor Authentication)
- Factors: Support TOTP (RFC 6238) first; design interfaces for SMS/Email/WebAuthn later.
- Enrollment: Endpoints to enroll, verify, and disable factors; recovery codes management.
- Enforcement: Policy to require MFA based on risk, group, or endpoint sensitivity.
- Storage: Persist MFA secrets securely; encrypt at rest.
- UX: Return clear error codes when additional verification is needed.

### Sessions
- Models: Session entity (id, user, issued_at, expires_at, ip, ua, mfa_level).
- Storage: Persistent session store with revocation and inactivity timeout.
- Middleware: Attach session to request context; refresh/rolling expiration rules.
- Security: Detect anomalous session behavior (IP/device change) and invalidate.
- Endpoints: Create, list, revoke sessions; self-service logout.

### Tokens
- Formats: Support JWT (access/refresh) with proper signing (RS256/ES256) and key rotation.
- Claims: Standard and custom claims (sub, iss, exp, iat, groups, scopes).
- Validation: Middleware to validate signature, expiry, audience; map to principal.
- Refresh: Implement refresh token flow with rotation & reuse detection.
- Introspection: Endpoint to verify token status/claims for services.
- Key management: JWKS endpoint and key rotation process; store KIDs.

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
