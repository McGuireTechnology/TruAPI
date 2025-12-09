# Quick Start: Adding Authorization to Your Bounded Context

## 1. Make Your Entity Authorization-Aware

```python
# api/documents/models.py
from dataclasses import dataclass, field
from typing import Optional
from api.core.authorization import ResourceOwnership

@dataclass
class Document(ResourceOwnership):
    id: DocumentId
    title: str
    content: str
    # Add these fields with defaults (required for dataclass)
    owner_type: str = field(default="user")
    owner_id: Optional[str] = field(default=None)
```

## 2. Set Ownership on Creation

```python
# api/documents/services.py
from api.core.authz import ResourceOwner, PermissionService

async def create_document(..., permission_service: PermissionService):
    # Create document
    doc = Document(
        id=DocumentId.new(),
        title=title,
        content=content,
        owner_type=owner_type,
        owner_id=owner_id
    )

    # Register with permission system
    owner = ResourceOwner.user(owner_id) if owner_type == "user" else ResourceOwner.group(owner_id)
    await permission_service.set_resource_owner("document", str(doc.id.value), owner)

    return doc
```

## 3. Check Permissions Before Operations

```python
from api.core.authz import Permission, PermissionService

async def get_document(document_id: str, user_id: str, permission_service: PermissionService):
    # Check READ permission
    has_perm, reason, _ = await permission_service.check_permission(
        "document", document_id, user_id, Permission.READ
    )
    if not has_perm:
        raise ValueError(f"Access denied: {reason}")

    # Proceed...
```

## 4. Permission Types

| Permission | Use For |
|------------|---------|
| `Permission.READ` | Viewing, listing, downloading |
| `Permission.WRITE` | Creating, updating, deleting |
| `Permission.EXECUTE` | Running, processing, special actions |

## 5. Common Permission Patterns

```python
# Private (owner only)
await permission_service.set_resource_permissions(
    "document", doc_id,
    owner_perms={Permission.READ, Permission.WRITE, Permission.EXECUTE},
    group_perms=set(),
    world_perms=set(),
    updated_by=user_id
)

# Team collaboration (owner + group can edit)
await permission_service.set_resource_permissions(
    "document", doc_id,
    owner_perms={Permission.READ, Permission.WRITE, Permission.EXECUTE},
    group_perms={Permission.READ, Permission.WRITE},
    world_perms=set(),
    updated_by=user_id
)

# Public read-only
await permission_service.set_resource_permissions(
    "document", doc_id,
    owner_perms={Permission.READ, Permission.WRITE, Permission.EXECUTE},
    group_perms={Permission.READ, Permission.EXECUTE},
    world_perms={Permission.READ},
    updated_by=user_id
)
```

That's it! Your bounded context now has full Unix-style authorization.
