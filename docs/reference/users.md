---
title: Users Reference
---

# Users

End‑to‑end reference for the Users slice: domain → use cases → ports → adapters → drivers.

## Domain

### Entity
::: api.domain.entities.user

## Use Cases
::: api.use_cases.user.create
::: api.use_cases.user.get
::: api.use_cases.user.update
::: api.use_cases.user.delete

## Ports
::: api.ports.repositories.user

## Adapters

### In‑Memory Repository
::: api.adapters.repositories.user.in_memory

### SQLAlchemy Repository
::: api.adapters.repositories.user.sqlalchemy

## Drivers (REST)
::: api.drivers.rest.routers.users

## OpenAPI

<swagger-ui src="openapi-users.json"></swagger-ui>
