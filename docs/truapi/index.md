# API Architecture

This document describes the high-level architecture and module boundaries of the API. Each section maps 1:1 to a Python package under `api/` and is tagged accordingly in OpenAPI.

## Identity & Access Management (IAM)
- Purpose: Unified module for identities (users, groups), authentication, and authorization (endpoint and resource permissions).
- Principals: `User`, `Group` (roles are represented as groups).
- Authentication: Password hashing, session/token flows; JWT settings scoped under `api.identity.settings`.
- Endpoint ACLs: Grants bind groups to cataloged endpoints from `api.platform.endpoints`; enforced via `authorize_endpoint(...)`.
- Resource DAC: Per-record checks using `owner_id`, `group_id`, and `mode` via `DACMixin`; enforced via `authorize_resource(...)`.
- Helpers: Request-time dependencies for current user and group resolution.
- Tags: `identity`, `iam`.

## Platform
- Purpose: System-level capabilities and catalogs.
- Endpoints Catalog: `api.platform.endpoints` provides `EndpointId`, method metadata, and discovery routes.
- Other: Room for app-level registries, feature flags, and platform status.
- Tags: `platform`.

## Storage
- Purpose: Data access providers and repositories.
- Scope: DB engines, repository interfaces, and in-memory adapters used by services.
- Notes: Business logic remains in domain services; storage abstracts persistence.
- Tags: `storage`.

## Shared
- Purpose: Cross-cutting utilities and base settings used by multiple modules.
- Scope: App settings, shared config helpers, generic storage abstractions.
- Tags: `shared`.

## Finance
- Purpose: Domain services, models, and routes for finance-related features.
- Scope: Business logic for invoices, payments, and reporting; depends on Identity and Storage.
- Tags: `finance`.

---

## Design Principles
- Modularity: Each module owns its router and service boundaries; aggregated via `api/routes.py`.
- Clear ACL layers: Endpoint ACLs enforced at router dependencies; resource ACLs enforced near data using DAC.
- Identity-first: Users and groups are the only principals; roles are groups.
- Replaceable storage: Start in-memory, migrate to SQLAlchemy without changing service contracts.
- Settings isolation: JWT and auth settings live under `api.identity.settings`; app/global settings under `api.settings`.

## Routing & Tags
- Aggregation: Top-level router includes `access_control`, `identity`, `platform`, `storage`, `finance`, `observability`.
- Tags: Each module sets its tag; OpenAPI groups are organized by module.

## Observability
- Purpose: Status and health endpoints; app/version/environment reporting.
- Routes: `/` (root status), `/health` (health check).
- Tags: `observability`.

## Next Steps
- Document per-module route summaries.
- Add OpenAPI tag groups for better navigation.
- Link to developer docs and API references for each module.
