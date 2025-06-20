"""Tests for market data tools."""

import pytest

from shioaji_mcp.tools.contracts import search_contracts
from shioaji_mcp.tools.market_data import get_kbars, get_snapshots
from shioaji_mcp.utils.auth import auth_manager


@pytest.mark.asyncio
async def test_search_contracts_not_logged_in():
    """Test contract search when not logged in."""
    # Ensure we're logged out
    await auth_manager.logout()

    result = await search_contracts({})

    assert len(result) == 1
    assert "Error: Not logged in" in result[0]["text"]


@pytest.mark.asyncio
async def test_search_contracts_success():
    """Test successful contract search."""
    # Login first
    await auth_manager.login(
        api_key="test_key",
        secret_key="test_secret",
        person_id="test_person",
        password="test_password",
    )

    result = await search_contracts({"keyword": "台積電"})

    assert len(result) == 2  # Success message + data
    assert "Found" in result[0]["text"]


@pytest.mark.asyncio
async def test_get_snapshots_missing_contracts():
    """Test snapshots with missing contracts."""
    # Ensure logged in
    await auth_manager.login(
        api_key="test_key",
        secret_key="test_secret",
        person_id="test_person",
        password="test_password",
    )

    result = await get_snapshots({})

    assert len(result) == 1
    assert "Error: No contracts specified" in result[0]["text"]


@pytest.mark.asyncio
async def test_get_snapshots_success():
    """Test successful snapshot retrieval."""
    # Ensure logged in
    await auth_manager.login(
        api_key="test_key",
        secret_key="test_secret",
        person_id="test_person",
        password="test_password",
    )

    result = await get_snapshots({"contracts": ["2330", "2317"]})

    assert len(result) == 2  # Success message + data
    assert "Retrieved snapshots for 2 contracts" in result[0]["text"]


@pytest.mark.asyncio
async def test_get_kbars_missing_contract():
    """Test K-bars with missing contract."""
    # Ensure logged in
    await auth_manager.login(
        api_key="test_key",
        secret_key="test_secret",
        person_id="test_person",
        password="test_password",
    )

    result = await get_kbars({})

    assert len(result) == 1
    assert "Error: Contract code is required" in result[0]["text"]


@pytest.mark.asyncio
async def test_get_kbars_success():
    """Test successful K-bar retrieval."""
    # Ensure logged in
    await auth_manager.login(
        api_key="test_key",
        secret_key="test_secret",
        person_id="test_person",
        password="test_password",
    )

    result = await get_kbars({"contract": "2330"})

    assert len(result) == 2  # Success message + data
    assert "Retrieved" in result[0]["text"] and "K-bars for 2330" in result[0]["text"]
