"""Tests for the medicines endpoints against the actual database."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_medicines(client: AsyncClient):
    resp = await client.get("/api/medicines")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert isinstance(data["items"], list)
    if len(data["items"]) > 0:
        first = data["items"][0]
        assert "med_no" in first
        assert "med_name" in first
        assert "total_stock" in first
        assert "status" in first


@pytest.mark.asyncio
async def test_list_medicines_with_filter(client: AsyncClient):
    resp = await client.get("/api/medicines?page=1&page_size=5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert len(data["items"]) <= 5


@pytest.mark.asyncio
async def test_get_medicine_not_found(client: AsyncClient):
    resp = await client.get("/api/medicines/9999999")
    assert resp.status_code == 404
    assert "detail" in resp.json()


@pytest.mark.asyncio
async def test_create_update_delete_medicine_flow(client: AsyncClient):
    # 1. Create
    payload = {
        "med_name": "Temporary Test Medicine",
        "category": "Capsule",
        "manufacturer": "Test Labs",
        "unit": "Strip of 10",
        "mrp": 99.50,
    }
    create_resp = await client.post("/api/medicines", json=payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    med_no = created["med_no"]
    assert created["med_name"] == payload["med_name"]
    assert created["total_stock"] == 0
    assert created["status"] == "out_of_stock"

    # 2. Get by ID
    get_resp = await client.get(f"/api/medicines/{med_no}")
    assert get_resp.status_code == 200
    assert get_resp.json()["med_no"] == med_no
    assert "batches" in get_resp.json()

    # 3. Update
    update_payload = {
        "med_name": "Updated Test Medicine",
        "category": "Tablet",
        "manufacturer": "Updated Labs",
        "unit": "Bottle",
        "mrp": 120.00,
    }
    update_resp = await client.put(f"/api/medicines/{med_no}", json=update_payload)
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["med_name"] == "Updated Test Medicine"
    assert updated["mrp"] == 120.00

    # 4. Delete
    delete_resp = await client.delete(f"/api/medicines/{med_no}")
    assert delete_resp.status_code == 204

    # 5. Verify 404 after delete
    get_after_delete = await client.get(f"/api/medicines/{med_no}")
    assert get_after_delete.status_code == 404


@pytest.mark.asyncio
async def test_delete_medicine_referenced_conflict(client: AsyncClient):
    """Deleting a medicine that has referencing batches should yield 409."""
    list_resp = await client.get("/api/medicines")
    items = list_resp.json()["items"]
    # Find an existing medicine with batches
    med_with_stock = next((m for m in items if m["total_stock"] > 0), None)
    if med_with_stock:
        del_resp = await client.delete(f"/api/medicines/{med_with_stock['med_no']}")
        assert del_resp.status_code == 409
        assert "Cannot delete: this record is in use" in del_resp.json()["detail"]

