"""Tests for trading operation tools."""

import pytest

from shioaji_mcp.tools.orders import cancel_order, list_orders, place_order
from shioaji_mcp.tools.positions import get_account_balance, get_positions
from shioaji_mcp.utils.auth import auth_manager


@pytest.mark.asyncio
async def test_place_order_not_logged_in():
    """Test place order when not logged in."""
    await auth_manager.logout()

    result = await place_order({})

    assert len(result) == 1
    assert "Error: Not logged in" in result[0]["text"]


@pytest.mark.asyncio
async def test_place_order_missing_params():
    """Test place order with missing parameters."""
    await auth_manager.login(
        api_key="test_key",
        secret_key="test_secret",
        person_id="test_person",
        password="test_password",
    )

    result = await place_order({})

    assert len(result) == 1
    assert "Missing required parameters" in result[0]["text"]


@pytest.mark.asyncio
async def test_place_order_success():
    """Test successful order placement."""
    await auth_manager.login(
        api_key="test_key",
        secret_key="test_secret",
        person_id="test_person",
        password="test_password",
    )

    result = await place_order(
        {"contract": "2330", "action": "Buy", "quantity": 1000, "price": 500.0}
    )

    assert len(result) == 2
    assert "Order placed successfully" in result[0]["text"]


@pytest.mark.asyncio
async def test_cancel_order_missing_id():
    """Test cancel order with missing order ID."""
    await auth_manager.login(
        api_key="test_key",
        secret_key="test_secret",
        person_id="test_person",
        password="test_password",
    )

    result = await cancel_order({})

    assert len(result) == 1
    assert "Order ID is required" in result[0]["text"]


@pytest.mark.asyncio
async def test_cancel_order_success():
    """Test successful order cancellation."""
    await auth_manager.login(
        api_key="test_key",
        secret_key="test_secret",
        person_id="test_person",
        password="test_password",
    )

    result = await cancel_order({"order_id": "ORD12345"})

    assert len(result) == 2
    assert "cancelled successfully" in result[0]["text"]


@pytest.mark.asyncio
async def test_list_orders_success():
    """Test successful order listing."""
    await auth_manager.login(
        api_key="test_key",
        secret_key="test_secret",
        person_id="test_person",
        password="test_password",
    )

    result = await list_orders({})

    assert len(result) == 2
    assert "Retrieved" in result[0]["text"] and "orders" in result[0]["text"]


@pytest.mark.asyncio
async def test_get_positions_success():
    """Test successful position retrieval."""
    await auth_manager.login(
        api_key="test_key",
        secret_key="test_secret",
        person_id="test_person",
        password="test_password",
    )

    result = await get_positions({})

    assert len(result) == 2
    assert "Retrieved" in result[0]["text"] and "positions" in result[0]["text"]


@pytest.mark.asyncio
async def test_get_account_balance_success():
    """Test successful account balance retrieval."""
    await auth_manager.login(
        api_key="test_key",
        secret_key="test_secret",
        person_id="test_person",
        password="test_password",
    )

    result = await get_account_balance({})

    assert len(result) == 2
    assert "Account balance retrieved" in result[0]["text"]
