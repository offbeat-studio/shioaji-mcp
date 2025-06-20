"""Tests for authentication utilities."""

import pytest

from shioaji_mcp.utils.auth import ShioajiAuth


@pytest.mark.asyncio
async def test_auth_login_success():
    """Test successful login."""
    auth = ShioajiAuth()

    result = await auth.login(
        api_key="test_key",
        secret_key="test_secret",
        person_id="test_person",
        password="test_password",
    )

    assert result["success"] is True
    assert "Login successful" in result["message"]
    assert auth.is_connected() is True


@pytest.mark.asyncio
async def test_auth_login_missing_credentials():
    """Test login with missing credentials."""
    auth = ShioajiAuth()

    result = await auth.login()

    assert result["success"] is False
    assert "Missing required credentials" in result["message"]
    assert auth.is_connected() is False


@pytest.mark.asyncio
async def test_auth_logout():
    """Test logout functionality."""
    auth = ShioajiAuth()

    # Login first
    await auth.login(
        api_key="test_key",
        secret_key="test_secret",
        person_id="test_person",
        password="test_password",
    )

    # Then logout
    result = await auth.logout()

    assert result["success"] is True
    assert auth.is_connected() is False


def test_get_api_not_connected():
    """Test getting API when not connected."""
    auth = ShioajiAuth()

    with pytest.raises(RuntimeError, match="Not connected to Shioaji API"):
        auth.get_api()
