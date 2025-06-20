"""Tests for the MCP server."""

import pytest

from shioaji_mcp.server import server


def test_server_creation():
    """Test that the server can be created."""
    assert server is not None
    assert server.name == "shioaji-mcp"


@pytest.mark.asyncio
async def test_list_tools():
    """Test that tools can be listed."""
    # Test the handler function directly
    from shioaji_mcp.server import handle_list_tools

    tools = await handle_list_tools()
    assert len(tools) >= 2

    tool_names = [tool.name for tool in tools]
    assert "shioaji_login" in tool_names
    assert "get_account_info" in tool_names
    assert "shioaji_logout" in tool_names
    assert "search_contracts" in tool_names
    assert "get_snapshots" in tool_names
    assert "get_kbars" in tool_names
    assert "place_order" in tool_names
    assert "cancel_order" in tool_names
    assert "list_orders" in tool_names
    assert "get_positions" in tool_names
    assert "get_account_balance" in tool_names
