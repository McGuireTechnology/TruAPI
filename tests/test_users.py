#! /usr/bin/env python
# ruff: noqa: E402
"""Users API tests.

The path manipulation before importing the application triggers Ruff's E402
 (module import not at top of file). We intentionally modify sys.path prior to
 importing to ensure the local 'api' directory is discoverable when tests are
 run from various working directories. Suppress E402 for this file.
"""

import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

# Ensure 'api' directory is on path so 'api' package can be imported when
# running tests from repository root or api subdirectory.
API_DIR = Path(__file__).resolve().parents[1]  # .../api
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from truapi.drivers.rest.main import app  # noqa: E402


@pytest.mark.asyncio
async def test_create_and_get_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post(
            "/users",
            json={
                "email": "alice@example.com",
                "first_name": "Alice",
                "last_name": "Anderson",
            },
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        user_id = data["id"]
        assert data["email"] == "alice@example.com"
        assert data["is_active"] is True

        # Get user
        get_resp = await ac.get(f"/users/{user_id}")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["id"] == user_id
        assert get_data["full_name"] == "Alice Anderson"


@pytest.mark.asyncio
async def test_list_users():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create two users
        for i in range(2):
            await ac.post(
                "/users",
                json={
                    "email": f"user{i}@example.com",
                    "first_name": f"User{i}",
                    "last_name": "Test",
                },
            )
        list_resp = await ac.get("/users")
        assert list_resp.status_code == 200
        data = list_resp.json()
        assert data["total"] >= 2
        assert len(data["users"]) >= 2


@pytest.mark.asyncio
async def test_update_deactivate_activate_delete_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create user
        create_resp = await ac.post(
            "/users",
            json={
                "email": "bob@example.com",
                "first_name": "Bob",
                "last_name": "Builder",
            },
        )
        user_id = create_resp.json()["id"]

        # Update profile
        update_resp = await ac.patch(
            f"/users/{user_id}",
            json={"first_name": "Robert"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["first_name"] == "Robert"

        # Deactivate
        deact_resp = await ac.post(f"/users/{user_id}/deactivate")
        assert deact_resp.status_code == 200
        assert deact_resp.json()["is_active"] is False

        # Activate
        act_resp = await ac.post(f"/users/{user_id}/activate")
        assert act_resp.status_code == 200
        assert act_resp.json()["is_active"] is True

        # Delete (must deactivate first)
        await ac.post(f"/users/{user_id}/deactivate")
        del_resp = await ac.delete(f"/users/{user_id}")
        assert del_resp.status_code == 200
        assert del_resp.json()["success"] is True

        # Confirm gone
        get_resp = await ac.get(f"/users/{user_id}")
        assert get_resp.status_code == 404
