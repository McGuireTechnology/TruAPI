# Users

End‑to‑end reference for the Users slice: domain → use cases → ports → adapters → drivers.

## Domain

### Entity

::: truapi.domains.entities.user

## Use Cases

::: truapi.use_cases.user.create
::: truapi.use_cases.user.get
::: truapi.use_cases.user.update
::: truapi.use_cases.user.delete

## Ports

::: truapi.ports.repositories.user

## Adapters

### In‑Memory Repository

::: truapi.adapters.repositories.user.in_memory

### SQLAlchemy Repository

::: truapi.adapters.repositories.user.sqlalchemy

## Drivers (REST)

::: truapi.drivers.rest.routers.users

## OpenAPI

<!-- Swagger JSON not present; embed removed to avoid build warnings. -->
