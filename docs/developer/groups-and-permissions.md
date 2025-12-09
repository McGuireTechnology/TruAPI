# Groups and Permissions System

## Overview

The Groups and Permissions system provides a Unix/Linux-style authorization framework for resource-based access control. It enables:

- **Groups**: Organizational units for users
- **Resource Ownership**: Resources are owned by a user or group (like Unix files)
- **Unix-style Permissions**: Read, Write, Execute (rwx) permissions for owner, group, and world
- **Familiar Model**: Uses the same permission model as Linux file systems (e.g., rwxr-x---)

## Architecture

The Groups module follows DDD and hexagonal architecture:

```
api/groups/
├── models.py                    # Domain entities (Group, Permission, ResourceOwner)
├── services.py                  # Business logic (GroupService, PermissionService)
├── repositories/                # Data access layer
│   ├── generic.py              # Repository interfaces (ports)
│   └── inmemory.py             # In-memory implementation (adapters)
├── routes.py                    # HTTP endpoints
├── schemas.py                   # Request/response DTOs
├── dependencies.py              # Dependency injection
└── auth/
    └── dependencies.py          # Authorization dependencies
```

## Domain Models

### Group

```python
@dataclass
class Group:
    id: GroupId                  # ULID identifier
    name: str                    # Unique group name
    description: str | None
    members: list[GroupMember]   # Group members with roles
    created_by: str              # User ULID who created it
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

### GroupMember

```python
@dataclass(frozen=True)
class GroupMember:
    user_id: str                 # User ULID
    role: GroupRole              # owner, admin, or member
    joined_at: datetime
```

### GroupRole (Enum)

- **OWNER**: Can manage group, add/remove members, delete group, manage permissions
- **ADMIN**: Can add/remove members, manage permissions
- **MEMBER**: Standard member, inherits group permissions on resources

### Permission (Enum)

Unix-style permissions (rwx):

- **READ**: Can view/read resources (r)
- **WRITE**: Can modify/update resources (w)
- **EXECUTE**: Can execute/run resources (x)

Permissions are set for three categories:
- **Owner**: The user or group that owns the resource
- **Group**: Members of the group (if resource is group-owned)
- **World**: Everyone else

### ResourceOwner

```python
@dataclass(frozen=True)
class ResourceOwner:
    owner_type: str              # "user" or "group"
    owner_id: str                # ULID of owner
```

### ResourcePermissions

```python
@dataclass(frozen=True)
class ResourcePermissions:
    resource_type: str           # e.g., "document", "project", "order"
    resource_id: str             # ULID of the resource
    owner_perms: set[Permission] # Permissions for owner (e.g., {READ, WRITE, EXECUTE})
    group_perms: set[Permission] # Permissions for group (e.g., {READ, EXECUTE})
    world_perms: set[Permission] # Permissions for everyone else (e.g., {READ})
    updated_at: datetime
    updated_by: str | None       # User ULID who last updated
```

**Example**: `rwxr-x---` means:
- Owner: read, write, execute (rwx)
- Group: read, execute (r-x)
- World: no permissions (---)

## API Endpoints

### Group Management

```
POST   /groups                   Create a new group
GET    /groups                   List all groups
GET    /groups/my-groups         List groups where user is a member
GET    /groups/{group_id}        Get group details
PATCH  /groups/{group_id}        Update group (admin/owner only)
DELETE /groups/{group_id}        Delete group (owner only)
```

### Member Management

```
### Permission Management

```
POST   /groups/permissions/set-owner              Set resource owner (user or group)
POST   /groups/permissions/set                    Set Unix-style permissions (rwx)
GET    /groups/permissions/{type}/{id}            Get permissions for a resource
POST   /groups/permissions/check                  Check if user has permission
```
POST   /groups/permissions/set-owner    Set resource owner
POST   /groups/permissions/grant        Grant permission
DELETE /groups/permissions/revoke       Revoke permission
POST   /groups/permissions/check        Check if user has permission
```

## Usage Examples

### Example 1: Create a Group

```python
# POST /groups
{
  "name": "Engineering Team",
  "description": "Software engineering team"
}

# Response
{
  "id": "01KBEJZZ9XA7N9KMTCGTXTFGBF",
  "name": "Engineering Team",
  "description": "Software engineering team",
  "created_by": "01KBEJYY8XA7N9KMTCGTXTFGBF",
  "is_active": true,
  "members": [
    {
      "user_id": "01KBEJYY8XA7N9KMTCGTXTFGBF",
      "role": "owner",
      "joined_at": "2025-12-01T10:30:00Z"
    }
  ],
  "member_count": 1,
  "created_at": "2025-12-01T10:30:00Z",
  "updated_at": "2025-12-01T10:30:00Z"
}
```

### Example 2: Add Members to Group

```python
# POST /groups/{group_id}/members
{
  "user_id": "01KBEK0A1BCD2EFGHIJK3LMNO4",
  "role": "member"
}
```

### Example 3: Set Resource Ownership

```python
# POST /groups/permissions/set-owner
{
  "resource_type": "document",
  "resource_id": "01KBEK1B2CDE3FGHIJK4LMNO5P",
  "owner_type": "group",
  "owner_id": "01KBEJZZ9XA7N9KMTCGTXTFGBF"
}

# Now the "Engineering Team" group owns this document
# This sets default permissions: rwxr-x--- (750)
# - Owner (group): read, write, execute
# - Group members: read, execute
# - World: no access
```

### Example 4: Set Unix-Style Permissions

```python
# Set permissions like Linux: rwxr-x--- (750)
# POST /groups/permissions/set
{
  "resource_type": "document",
  "resource_id": "01KBEK1B2CDE3FGHIJK4LMNO5P",
  "owner_perms": "rwx",    # Owner can read, write, execute
  "group_perms": "r-x",    # Group members can read and execute
  "world_perms": "---"     # No public access
}

# Response
{
  "resource_type": "document",
  "resource_id": "01KBEK1B2CDE3FGHIJK4LMNO5P",
  "owner_perms": "rwx",
  "group_perms": "r-x",
  "world_perms": "---",
  "permissions_string": "rwxr-x---",  # Like 'ls -l' output
  "updated_at": "2025-12-01T10:30:00Z",
  "updated_by": "01KBEJYY8XA7N9KMTCGTXTFGBF"
}

# Other common permission patterns:
# rwxr-xr-x (755) - Owner full, group/world can read+execute
# rw-r--r-- (644) - Owner read+write, group/world read-only
# rwx------ (700) - Owner only, no group or world access
# rw-rw-r-- (664) - Owner+group can write, world read-only
```

### Example 5: Check Permission

```python
# POST /groups/permissions/check
{
  "resource_type": "document",
  "resource_id": "01KBEK1B2CDE3FGHIJK4LMNO5P",
  "user_id": "01KBEK0A1BCD2EFGHIJK3LMNO4",
  "permission": "update"
}

# Response
{
  "has_permission": true,
  "reason": "User is in owning group 'Engineering Team'",
  "via": "group"
}
```

## Permission Resolution Logic (Unix-style)

When checking if a user has permission on a resource, the system uses Unix/Linux logic:

1. **Owner Check**: Is the user the owner? → Check owner permissions (rwx)
2. **Group Check**: Is the user in the owning group? → Check group permissions (rwx)
3. **World Check**: Everyone else → Check world permissions (rwx)

**Example**:
- Resource: `document:123` with permissions `rwxr-x---` (750)
- Owner: `user:alice`
- Group: `group:engineering`

**Scenarios**:
- Alice (owner) trying to write → ✅ Allowed (owner has `w`)
- Bob (engineering member) trying to read → ✅ Allowed (group has `r`)
- Bob (engineering member) trying to write → ❌ Denied (group lacks `w`)
- Charlie (not owner, not in group) trying to read → ❌ Denied (world has no permissions)

## Using Authorization in Your Bounded Context

### Option 1: Use Authorization Dependencies (Recommended)

```python
# In your bounded context routes (e.g., api/documents/routes.py)
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from api.users.auth.dependencies import get_current_user
from api.users.models import User
@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    permission_service: PermissionService = Depends(get_permission_service),
):
    """Get document (requires READ permission)"""
    # Check READ permission (r)
    user_id = str(current_user.id.value)
    has_permission, reason, via = await permission_service.check_permission(
        "document", document_id, user_id, Permission.READ
    )

    if not has_permission:
        raise HTTPException(status_code=403, detail=f"Access denied: {reason}")

    # User has permission - proceed with operation
    document = await document_service.get_document(document_id)
    return document


@router.patch("/{document_id}")
async def update_document(
    document_id: str,
    body: DocumentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    permission_service: PermissionService = Depends(get_permission_service),
):
    """Update document (requires WRITE permission)"""
    user_id = str(current_user.id.value)
    has_permission, _, _ = await permission_service.check_permission(
        "document", document_id, user_id, Permission.WRITE
    )

    if not has_permission:
        raise HTTPException(status_code=403, detail="Write permission required")

    # Proceed with update
    document = await document_service.update_document(document_id, body)
    return document


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    permission_service: PermissionService = Depends(get_permission_service),
):
    """Delete document (requires WRITE permission)"""
    user_id = str(current_user.id.value)
    has_permission, _, _ = await permission_service.check_permission(
        "document", document_id, user_id, Permission.WRITE
    )

    if not has_permission:
        raise HTTPException(status_code=403, detail="Write permission required")

    # Proceed with deletion
    await document_service.delete_document(document_id)
    return {"message": "Document deleted"}Permission.DELETE
    )

    if not has_permission:
        raise HTTPException(status_code=403, detail="Delete permission required")

    # Proceed with deletion
    await document_service.delete_document(document_id)
    return {"message": "Document deleted"}
```

### Option 2: Set Ownership on Resource Creation

```python
# When creating a resource, set ownership
@router.post("/documents")
async def create_document(
    body: DocumentCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    document_service: DocumentService = Depends(get_document_service),
    permission_service: PermissionService = Depends(get_permission_service),
):
    """Create a new document"""
    # Create the document
    document = await document_service.create_document(
        title=body.title,
        content=body.content,
        created_by=str(current_user.id.value)
    )

    # Set ownership (user or group)
    if body.owner_type == "group":
        owner = ResourceOwner.group(body.owner_group_id)
    else:
        owner = ResourceOwner.user(str(current_user.id.value))

    await permission_service.set_resource_owner(
        "document",
        str(document.id.value),
        owner
    )

    return document
```

### Option 3: Service-Level Permission Checks

```python
# In your service layer (e.g., api/documents/services.py)
from api.core.authz import Permission, PermissionService

class DocumentService:
    async def get_document(self, document_id: str, user_id: str) -> Document:
        """Get document with permission check"""
        # Check READ permission (r) at service level
        has_permission, reason, _ = await self._permission_service.check_permission(
            "document", document_id, user_id, Permission.READ
        )

        if not has_permission:
            raise ValueError(f"Access denied: {reason}")

        document = await self._document_repository.find_by_id(document_id)
        if not document:
            raise ValueError("Document not found")

        return document
        if not has_permission:
            raise ValueError(f"Access denied: {reason}")

        document = await self._document_repository.find_by_id(document_id)
        if not document:
            raise ValueError("Document not found")

        return document
```

## Best Practices

### 1. Always Set Ownership on Resource Creation

```python
# When creating a resource, ALWAYS set ownership
await permission_service.set_resource_owner(
    resource_type="document",
    resource_id=str(document.id.value),
    owner=ResourceOwner.user(str(current_user.id.value))
)
```

### 2. Use Groups for Team-Based Access

```python
# Create a project group
group = await group_service.create_group(
    name="Project Alpha Team",
    description="Team working on Project Alpha",
    created_by=str(current_user.id.value)
)

# Set group as owner of all project resources
await permission_service.set_resource_owner(
    "project",
    str(project.id.value),
    ResourceOwner.group(str(group.id.value))
)

# All group members automatically get access
```

### 3. Use Appropriate Permission Levels

```python
# Common permission patterns:

# Read-only for world (public documents)
await permission_service.set_resource_permissions(
    "document", document_id,
    owner_perms={Permission.READ, Permission.WRITE, Permission.EXECUTE},
    group_perms={Permission.READ, Permission.EXECUTE},
    world_perms={Permission.READ},  # Everyone can read
    updated_by=str(current_user.id.value)
)

# Group collaboration (team documents)
await permission_service.set_resource_permissions(
    "document", document_id,
    owner_perms={Permission.READ, Permission.WRITE, Permission.EXECUTE},
    group_perms={Permission.READ, Permission.WRITE},  # Team can edit
    world_perms=set(),  # No public access
    updated_by=str(current_user.id.value)
)

# Private (owner-only)
await permission_service.set_resource_permissions(
    "document", document_id,
    owner_perms={Permission.READ, Permission.WRITE, Permission.EXECUTE},
    group_perms=set(),  # No group access
    world_perms=set(),  # No public access
    updated_by=str(current_user.id.value)
)
```

### 4. Use Group Roles Appropriately

- **OWNER**: Critical operations (delete group, change ownership)
- **ADMIN**: Day-to-day management (add/remove members)
- **MEMBER**: Standard access (inherits permissions)

### 5. Check Permissions Early

```python
# Check permission BEFORE doing expensive operations
has_permission, _, _ = await permission_service.check_permission(...)
if not has_permission:
    raise HTTPException(status_code=403, detail="Access denied")

# Only proceed if authorized
result = await expensive_operation()
```

## Database Schema (for SQLAlchemy)

When implementing SQLAlchemy adapters, use these table structures:

```sql
-- Groups table
CREATE TABLE groups (
    id VARCHAR(26) PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(500),
    created_by VARCHAR(26) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Group members table
-- Resource permissions table (Unix-style)
CREATE TABLE resource_permissions (
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(26) NOT NULL,
    owner_perms VARCHAR(3) NOT NULL,    -- e.g., 'rwx', 'r-x', 'rw-'
    group_perms VARCHAR(3) NOT NULL,    -- e.g., 'r-x', 'r--', '---'
    world_perms VARCHAR(3) NOT NULL,    -- e.g., 'r--', '---'
    updated_at TIMESTAMP NOT NULL,
    updated_by VARCHAR(26),
    PRIMARY KEY (resource_type, resource_id)
);EATE TABLE resource_owners (
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(26) NOT NULL,
    owner_type VARCHAR(10) NOT NULL,
    owner_id VARCHAR(26) NOT NULL,
    PRIMARY KEY (resource_type, resource_id)
);

-- Resource permissions table
CREATE TABLE resource_permissions (
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(26) NOT NULL,
async def test_owner_has_full_permissions():
    """Test that resource owner respects owner permissions"""
    # Set user as owner
    await permission_service.set_resource_owner(
        "document", "doc123", ResourceOwner.user("user123")
    )

    # Set permissions: rwx for owner
    await permission_service.set_resource_permissions(
        "document", "doc123",
        owner_perms={Permission.READ, Permission.WRITE, Permission.EXECUTE},
        group_perms=set(),
        world_perms=set(),
        updated_by="user123"
    )

    # Owner should have all granted permissions
    for perm in [Permission.READ, Permission.WRITE, Permission.EXECUTE]:
        has_perm, _, via = await permission_service.check_permission(
            "document", "doc123", "user123", perm
        )
        assert has_perm, f"Owner should have {perm} permission"
        assert via == "owner"


async def test_group_member_permissions():
    """Test that group members get group permissions only"""
    # Create group with member
    group = await group_service.create_group("Team", None, "owner123")
    await group_service.add_member(group.id, "member456", GroupRole.MEMBER, "owner123")

    # Set group as owner
    await permission_service.set_resource_owner(
        "document", "doc123", ResourceOwner.group(str(group.id.value))
    )
## Summary

The Groups and Permissions system provides:

✅ **Unix/Linux-style authorization** - Familiar rwx permission model
✅ **Simple and clear** - Read, Write, Execute for owner/group/world
✅ **Team collaboration** - Groups enable team-based access
✅ **Flexible ownership** - Resources owned by users or groups
✅ **World permissions** - Control public access like Unix files
✅ **Extensible** - Easy to add to any bounded context

**Permission patterns at a glance**:
- `rwx------` (700): Private, owner-only
- `rwxr-x---` (750): Owner full, group read+execute
- `rw-rw----` (660): Owner+group can edit, no public
- `rw-r--r--` (644): Owner edits, everyone can read
- `rwxr-xr-x` (755): Owner full, everyone can read+execute

Use this system for any resource that needs access control beyond simple ownership!
        "document", "doc123", "member456", Permission.READ
    )
    assert has_read
    assert via == "group"

    # Member should NOT have WRITE (not in group perms)
    has_write, _, _ = await permission_service.check_permission(
        "document", "doc123", "member456", Permission.WRITE
    )
    assert not has_write


async def test_world_permissions():
    """Test that non-members get world permissions"""
    # Set owner
    await permission_service.set_resource_owner(
        "document", "doc123", ResourceOwner.user("owner123")
    )

    # Set world-readable permissions
    await permission_service.set_resource_permissions(
        "document", "doc123",
        owner_perms={Permission.READ, Permission.WRITE, Permission.EXECUTE},
        group_perms={Permission.READ, Permission.EXECUTE},
        world_perms={Permission.READ},  # World can read
        updated_by="owner123"
    )

    # Random user should have READ (world perms)
    has_read, _, via = await permission_service.check_permission(
        "document", "doc123", "random_user", Permission.READ
    )
    assert has_read
    assert via == "world"

    # Random user should NOT have WRITE
    has_write, _, _ = await permission_service.check_permission(
        "document", "doc123", "random_user", Permission.WRITE
    )
    assert not has_write
async def test_group_member_inherits_permissions():
    """Test that group members inherit group permissions"""
    # Create group with member
    group = await group_service.create_group("Team", None, "owner123")
    await group_service.add_member(group.id, "member456", GroupRole.MEMBER, "owner123")

    # Grant permission to group
    await permission_service.grant_permission(
        "document", "doc123", "group", str(group.id.value),
        Permission.READ, "owner123"
    )

    # Member should have permission
    has_perm, _, via = await permission_service.check_permission(
        "document", "doc123", "member456", Permission.READ
    )
    assert has_perm
    assert "group" in via
```

## Summary

The Groups and Permissions system provides:

✅ **Flexible authorization** - Users and groups can own resources
✅ **Fine-grained control** - CREATE, READ, UPDATE, DELETE permissions
✅ **Team collaboration** - Groups enable team-based access
✅ **Inheritance** - Group members inherit group permissions
✅ **Auditable** - Track who granted permissions and when
✅ **Extensible** - Easy to add to any bounded context

Use this system for any resource that needs access control beyond simple ownership!
