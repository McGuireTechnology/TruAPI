# Developer

This project follows a hexagonal (ports & adapters) architecture with clear boundaries between the core domain and external systems to maximize testability and maintainability.

## Domains

- Purpose: Encapsulate business concepts, rules, and invariants. Pure Python with no framework dependencies.
- Contents: Entities (e.g., `User`), Value Objects (e.g., `ID`), and domain logic.
- Guarantees: Deterministic and side-effect free; unit-testable without IO.

## Use Cases

- Purpose: Application services that orchestrate domain behavior and enforce workflows.
- Shape: Small functions/classes (e.g., `create`, `get`, `update`, `delete`) that accept ports and domain DTOs.
- Errors: Raise explicit exceptions for predictable failures (e.g., not found, conflicts).

## Ports

- Purpose: Stable interfaces the core depends on to talk to the outside world.
- Examples: Repository interfaces (e.g., `UserRepository`, `SettingsRepository`).
- Rule: Core imports ports, never concrete adapters; enables easy swapping of implementations.

## Adapters

- Purpose: Concrete implementations of ports to interact with external systems.
- Examples: In-memory repositories for tests; SQLAlchemy repositories for databases; HTTP clients.
- Constraint: Adapters depend on libraries/frameworks and live at the edges; they do not leak into the core.

## Drivers

- Purpose: Entry points that expose the application (REST, CLI, jobs).
- Examples: FastAPI routers/controllers, background workers.
- Role: Validate inputs, call use cases, map domain outputs to transport-friendly responses.

## Development Pattern

- Define domain models and invariants.
- Specify ports for persistence/integrations.
- Implement use cases operating on domain via ports.
- Provide adapters that satisfy ports (SQLAlchemy, in-memory, etc.).
- Expose drivers (REST endpoints) that call use cases with adapter instances.
- Test inside-out: domain → use cases → adapters → drivers.

## Benefits

- Testability: Core logic is easy to test without infrastructure.
- Replaceability: Swap adapters without touching the core (e.g., change DB).
- Separation: Each layer has a single responsibility.
- Evolvability: Add features by composing use cases and ports, keeping the domain clean.

## Vertical Slice (Mermaid)

```mermaid
flowchart TD
 subgraph Driver[Drivers]
  R[REST Router (FastAPI)]
 end

 subgraph UseCases[Use Cases]
  UC_Create[create(user)]
  UC_Get[get(user)]
  UC_Update[update(user)]
  UC_Delete[delete(user)]
 end

 subgraph Ports[Ports]
  PR[UserRepository]
  SR[SettingsRepository]
 end

 subgraph Adapters[Adapters]
  IM[InMemoryUserRepository]
  SA[SQLAlchemyUserRepository]
  SIM[InMemorySettingsRepository]
 end

 subgraph Domain[Domain]
  U[User Entity]
  VID[ID ValueObject]
 end

 R --> UC_Create
 R --> UC_Get
 R --> UC_Update
 R --> UC_Delete

 UC_Create --> PR
 UC_Get --> PR
 UC_Update --> PR
 UC_Delete --> PR
 UC_Create -. config .-> SR

 PR -->|implements| IM
 PR -->|implements| SA
 SR -->|implements| SIM

 UC_Create --> U
 UC_Get --> U
 UC_Update --> U
 UC_Delete --> U
 U --> VID

 classDef core fill:#dff,stroke:#0af,stroke-width:1px;
 classDef edge fill:#ffd,stroke:#fa0,stroke-width:1px;
 class Domain,UseCases,Ports core;
 class Adapters,Driver edge;
```
