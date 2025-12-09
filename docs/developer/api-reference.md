# API Reference

This reference is generated from Python docstrings using MkDocs + mkdocstrings.

Below, modules are grouped by vertical slice so you can see each feature end‑to‑end (domain → use cases → ports → adapters → drivers).

## Users

### Domain

#### Entity
::: api.domain.entities.user

### Use Cases
::: api.use_cases.user.create
::: api.use_cases.user.get
::: api.use_cases.user.update
::: api.use_cases.user.delete

### Ports
::: api.ports.repositories.user

### Adapters
#### In-Memory Repository
::: api.adapters.repositories.user.in_memory

#### SQLAlchemy Repository
::: api.adapters.repositories.user.sqlalchemy

### Drivers (REST)
::: api.drivers.rest.routers.users

## Core

### Value Objects
::: api.domain.value_objects.id

### Shared Exceptions (Use Cases)
::: api.use_cases.exceptions
