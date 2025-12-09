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
