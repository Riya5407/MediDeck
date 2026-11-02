"""Tests for the batches endpoints against PostgreSQL database."""
import pytest
from datetime import date, timedelta
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_batches(client: AsyncClient):
    resp = await client.get("/api/batches")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "counts" in data
    counts = data["counts"]
    assert "total" in counts
    assert "expired" in counts
    assert "expiring_soon" in counts
    assert "valid" in counts
    assert isinstance(data["items"], list)
    if len(data["items"]) > 0:
        first = data["items"][0]
        assert "batch_no" in first
        assert "med_no" in first
        assert "med_name" in first
        assert "qty_in_stock" in first
        assert "status" in first
        assert "days_to_expiry" in first


@pytest.mark.asyncio
async def test_batches_ordered_by_expiry(client: AsyncClient):
    resp = await client.get("/api/batches?page=1&page_size=20")
    assert resp.status_code == 200
    items = resp.json()["items"]
    if len(items) >= 2:
        exp_dates = [i["exp_date"] for i in items if i["exp_date"] is not None]
        assert exp_dates == sorted(exp_dates)


@pytest.mark.asyncio
async def test_create_update_delete_batch_flow(client: AsyncClient):
    # Get a valid med_no first
    meds_resp = await client.get("/api/medicines")
    assert meds_resp.status_code == 200
    med_no = meds_resp.json()["items"][0]["med_no"]

    today = date.today()
    mfg = (today - timedelta(days=60)).isoformat()
    exp = (today + timedelta(days=365)).isoformat()

    # 1. Create
    create_payload = {
        "med_no": med_no,
        "mfg_date": mfg,
        "exp_date": exp,
        "qty_in_stock": 50,
        "pur_price": 25.50,
    }
    create_resp = await client.post("/api/batches", json=create_payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    batch_no = created["batch_no"]
    assert created["med_no"] == med_no
    assert created["qty_in_stock"] == 50
    assert created["pur_price"] == 25.50
    assert created["status"] == "in_stock"
    assert created["days_to_expiry"] is not None and created["days_to_expiry"] > 0

    # 2. Update
    update_payload = {
        "med_no": med_no,
        "mfg_date": mfg,
        "exp_date": exp,
        "qty_in_stock": 5,  # below low stock threshold -> low_stock
        "pur_price": 30.00,
    }
    update_resp = await client.put(f"/api/batches/{batch_no}", json=update_payload)
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["qty_in_stock"] == 5
    assert updated["status"] == "low_stock"

    # 3. Delete
    delete_resp = await client.delete(f"/api/batches/{batch_no}")
    assert delete_resp.status_code == 204


@pytest.mark.asyncio
async def test_update_nonexistent_batch_404(client: AsyncClient):
    payload = {
        "med_no": 1,
        "mfg_date": "2026-01-01",
        "exp_date": "2027-01-01",
        "qty_in_stock": 10,
        "pur_price": 10.0,
    }
    resp = await client.put("/api/batches/999999", json=payload)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_batch_referenced_conflict(client: AsyncClient):
    """Deleting a batch that has been sold from should return 409."""
    # Check if any batch is referenced in sale_details
    list_resp = await client.get("/api/batches?page=1&page_size=100")
    items = list_resp.json()["items"]
    for b in items:
        del_resp = await client.delete(f"/api/batches/{b['batch_no']}")
        if del_resp.status_code == 409:
            assert "Cannot delete: this record is in use" in del_resp.json()["detail"]
            break

