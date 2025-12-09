# Core Authorization Infrastructure

## Overview

The `api/core/authorization/` module provides reusable templates for adding Unix-style ownership and permissions to resources in any bounded context.

## Components

### `ResourceOwnership` Mixin

A dataclass mixin that adds `owner_type` and `owner_id` fields to your domain entities.

```python
from dataclasses import dataclass
from api.core.authorization import ResourceOwnership

@dataclass
class Document(ResourceOwnership):
    id: DocumentId
    title: str
    content: str
    # Inherits: owner_type, owner_id

# Usage
doc = Document(
    id=doc_id,
    title="Project Plan",
    content="...",
    owner_type="user",
    owner_id="01KBEJYY8XA7N9KMTCGTXTFGBF"
)

# Helper methods
if doc.is_owned_by_user(current_user_id):
    print("You own this document")

doc.set_group_owner(group_id)  # Change ownership to group
```

### Schema Mixins (Optional)

For Pydantic DTOs:

```python
from pydantic import BaseModel
from api.core.authorization.schemas import ResourceOwnershipSchema

class DocumentResponse(ResourceOwnershipSchema):
    id: str
    title: str
    content: str
    # Inherits: owner_type, owner_id
```

## Full Example: Documents Bounded Context

### Step 1: Domain Model

```python
# api/documents/models.py
from dataclasses import dataclass
from datetime import datetime
from api.core.authorization import ResourceOwnership

@dataclass
class Document(ResourceOwnership):
    """Document entity with ownership"""
    id: DocumentId
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    # owner_type and owner_id from ResourceOwnership
```

### Step 2: Service Layer

```python
# api/documents/services.py
from api.core.authz import Permission, ResourceOwner, PermissionService

class DocumentService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        permission_service: PermissionService
    ):
        self._documents = document_repository
        self._permissions = permission_service

    async def create_document(
        self,
        title: str,
        content: str,
        owner_type: str,
        owner_id: str,
        created_by: str
    ) -> Document:
        """Create document and set ownership"""
        # Create document
        doc = Document(
            id=DocumentId.new(),
            title=title,
            content=content,
            owner_type=owner_type,
            owner_id=owner_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        await self._documents.save(doc)

        # Set ownership in permission system
        if owner_type == "user":
            owner = ResourceOwner.user(owner_id)
        else:
            owner = ResourceOwner.group(owner_id)

        await self._permissions.set_resource_owner(
            "document",
            str(doc.id.value),
            owner
        )

        return doc

    async def get_document(
        self,
        document_id: str,
        user_id: str
    ) -> Document:
        """Get document with permission check"""
        # Check READ permission
        has_permission, reason, _ = await self._permissions.check_permission(
            "document", document_id, user_id, Permission.READ
        )

        if not has_permission:
            raise ValueError(f"Access denied: {reason}")

        doc = await self._documents.find_by_id(document_id)
        if not doc:
            raise ValueError("Document not found")

        return doc

    async def update_document(
        self,
        document_id: str,
        user_id: str,
        title: str | None = None,
        content: str | None = None
    ) -> Document:
        """Update document with permission check"""
        # Check WRITE permission
        has_permission, reason, _ = await self._permissions.check_permission(
            "document", document_id, user_id, Permission.WRITE
        )

        if not has_permission:
            raise ValueError(f"Access denied: {reason}")

        doc = await self._documents.find_by_id(document_id)
        if not doc:
            raise ValueError("Document not found")

        if title is not None:
            doc.title = title
        if content is not None:
            doc.content = content

        doc.updated_at = datetime.now(timezone.utc)
        await self._documents.save(doc)

        return doc
```

### Step 3: Routes

```python
# api/documents/routes.py
from fastapi import APIRouter, Depends, HTTPException
from api.users.auth.dependencies import get_current_user

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("", response_model=DocumentResponse)
async def create_document(
    body: DocumentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: DocumentService = Depends(get_document_service),
):
    """Create a new document"""
    try:
        # Default to user ownership if not specified
        owner_type = body.owner_type or "user"
        owner_id = body.owner_id or str(current_user.id.value)

        doc = await service.create_document(
            title=body.title,
            content=body.content,
            owner_type=owner_type,
            owner_id=owner_id,
            created_by=str(current_user.id.value)
        )

        return DocumentResponse(
            id=str(doc.id.value),
            title=doc.title,
            content=doc.content,
            owner_type=doc.owner_type,
            owner_id=doc.owner_id,
            created_at=doc.created_at,
            updated_at=doc.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    service: DocumentService = Depends(get_document_service),
):
    """Get document (requires READ permission)"""
    try:
        doc = await service.get_document(
            document_id,
            str(current_user.id.value)
        )

        return DocumentResponse(
            id=str(doc.id.value),
            title=doc.title,
            content=doc.content,
            owner_type=doc.owner_type,
            owner_id=doc.owner_id,
            created_at=doc.created_at,
            updated_at=doc.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    body: DocumentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: DocumentService = Depends(get_document_service),
):
    """Update document (requires WRITE permission)"""
    try:
        doc = await service.update_document(
            document_id,
            str(current_user.id.value),
            title=body.title,
            content=body.content
        )

        return DocumentResponse(
            id=str(doc.id.value),
            title=doc.title,
            content=doc.content,
            owner_type=doc.owner_type,
            owner_id=doc.owner_id,
            created_at=doc.created_at,
            updated_at=doc.updated_at
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
```

## Permissions Management

After creating a resource, you can manage its permissions using the Groups API:

```python
# Set Unix-style permissions (rwxr-x---)
POST /groups/permissions/set
{
  "resource_type": "document",
  "resource_id": "01KBEK1B2CDE3FGHIJK4LMNO5P",
  "owner_perms": "rwx",
  "group_perms": "r-x",
  "world_perms": "---"
}

# Change ownership
POST /groups/permissions/set-owner
{
  "resource_type": "document",
  "resource_id": "01KBEK1B2CDE3FGHIJK4LMNO5P",
  "owner_type": "group",
  "owner_id": "01KBEJZZ9XA7N9KMTCGTXTFGBF"
}
```

## Benefits

✅ **DRY**: Define ownership once in core, use everywhere
✅ **Consistent**: All resources have the same ownership model
✅ **Type-safe**: Dataclass mixin provides type checking
✅ **Helper methods**: Built-in utilities for common ownership checks
✅ **Optional**: Bounded contexts can choose to use it or not

## When to Use

Use `ResourceOwnership` when:
- Your resource needs access control
- Multiple users/teams should collaborate on the resource
- You want Unix-style permissions (rwx for owner/group/world)

Don't use it when:
- Resource is public/unprotected
- Resource is always owned by the authenticated user (simpler to just store `created_by`)
- You need a different authorization model
