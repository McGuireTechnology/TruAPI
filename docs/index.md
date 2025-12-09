# McGuire Technology Core API

The McGuire Technology Core API is the early foundation for building resource‑management applications at McGuire Technology, LLC. It focuses on a clean, modular architecture that can scale from a single API into multiple application contexts. Core modules live under `api/core/*` and provide shared capabilities such as authentication, users, groups, tokens, and permissions.

## Vision
- Build a reliable core API that other apps can reuse.
- Develop initial app contexts inside this repository, then graduate them into standalone applications when they mature.
- Standardize primitives for identity, authorization, and resource management to speed up future app development.

## Architecture Highlights
- Core Contexts: `api/core/*` contains reusable modules (authn, users, groups, tokens, endpoints, mfa).
- DAC Permissions: Inline discretionary access control fields (owner_id, group_id, mode) via `api.core.dacs`.
- ACL Ready: External ACL primitives in `api.core.acls` for future fine‑grained overrides.
- OpenAPI First: Sorted operations, enriched tags, and interactive docs at `/docs` and `/redoc`.
- Hexagonal Style: Boundaries between core and app contexts to reduce coupling and circular dependencies.

## Platform Architecture
- Independent Frontends: Web/mobile clients can be developed and deployed separately, calling into the shared Core API.
- Common API: A single, multi‑tenant API reduces duplication and centralizes identity, permissions, and resource management.
- Lower Hosting Costs: Early-stage apps share infrastructure (API, DB, auth) until they mature and graduate to dedicated services.
- Clear Contracts: OpenAPI + interactive docs enable frontend teams to iterate quickly against stable endpoints.

## Getting Started
- Dev server: `make dev` (defaults to port 8000; pass `PORT=8080` as needed).
- Interactive docs:
	- Swagger UI: `/docs`
	- ReDoc: `/redoc`
	- Redocly Playground (Try It): `/redoc-playground`
- Health: `/health` and root `/` provide status and version.

## Core Modules
- `Users`: CRUD, authentication dependencies, DTOs, and services.
- `Tokens`: Access and refresh tokens, JWT helpers, OAuth2 bearer scheme.
- `Groups`: Group resources with DAC fields and update flows.
- `Permissions`: Providers and services to evaluate DAC/ACL (extensible).
- `MFA`: Multi‑factor routes and services (extensible).
- `Endpoints`: Registry of outbound integrations.

## OpenAPI Enhancements
- Tags: Curated tag metadata with `externalDocs` for quick navigation.
- Tag Groups: `x-tagGroups` organize Identity, Access, Integration.
- Code Samples: `x-codeSamples` (curl, Python) on operations.
- Branding: `info.x-logo` for consistent header.
- Servers: Local/dev/prod presets to streamline Try It.

## Roadmap
- Graduate app contexts (e.g., Inventory, Content, Projects) into dedicated services.
- Extend ACL evaluation and admin endpoints for fine‑grained permissions.
- Harden auth flows (sessions, API keys, MFA) and add audit trails.
- Expand test coverage and performance profiling as modules evolve.

## Contributing
- Keep changes minimal and focused; avoid broad refactors in unrelated areas.
- Respect module boundaries: core code should not import domain entities from app contexts.
- Prefer small PRs with updated docs and tests.

## License
Copyright © McGuire Technology, LLC. All rights reserved.
