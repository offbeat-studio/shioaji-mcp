"""Tests for trading permissions."""

import os
import pytest
from unittest.mock import patch

from src.shioaji_mcp.utils.permissions import is_trading_enabled, check_trading_permission


class TestTradingPermissions:
    """Test trading permission checks."""

    def test_trading_disabled_by_default(self):
        """Test that trading is disabled by default."""
        with patch.dict(os.environ, {}, clear=True):
            assert not is_trading_enabled()

    def test_trading_enabled_with_true(self):
        """Test trading enabled with 'true' value."""
        with patch.dict(os.environ, {'SHIOAJI_TRADING_ENABLED': 'true'}):
            assert is_trading_enabled()

    def test_trading_enabled_with_1(self):
        """Test trading enabled with '1' value."""
        with patch.dict(os.environ, {'SHIOAJI_TRADING_ENABLED': '1'}):
            assert is_trading_enabled()

    def test_trading_enabled_with_yes(self):
        """Test trading enabled with 'yes' value."""
        with patch.dict(os.environ, {'SHIOAJI_TRADING_ENABLED': 'yes'}):
            assert is_trading_enabled()

    def test_trading_enabled_with_on(self):
        """Test trading enabled with 'on' value."""
        with patch.dict(os.environ, {'SHIOAJI_TRADING_ENABLED': 'on'}):
            assert is_trading_enabled()

    def test_trading_disabled_with_false(self):
        """Test trading disabled with 'false' value."""
        with patch.dict(os.environ, {'SHIOAJI_TRADING_ENABLED': 'false'}):
            assert not is_trading_enabled()

    def test_trading_disabled_with_0(self):
        """Test trading disabled with '0' value."""
        with patch.dict(os.environ, {'SHIOAJI_TRADING_ENABLED': '0'}):
            assert not is_trading_enabled()

    def test_trading_disabled_with_invalid_value(self):
        """Test trading disabled with invalid value."""
        with patch.dict(os.environ, {'SHIOAJI_TRADING_ENABLED': 'maybe'}):
            assert not is_trading_enabled()

    def test_case_insensitive_true(self):
        """Test case insensitive 'TRUE' value."""
        with patch.dict(os.environ, {'SHIOAJI_TRADING_ENABLED': 'TRUE'}):
            assert is_trading_enabled()

    def test_case_insensitive_false(self):
        """Test case insensitive 'FALSE' value."""
        with patch.dict(os.environ, {'SHIOAJI_TRADING_ENABLED': 'FALSE'}):
            assert not is_trading_enabled()

    def test_check_trading_permission_allowed(self):
        """Test trading permission when allowed."""
        with patch.dict(os.environ, {'SHIOAJI_TRADING_ENABLED': 'true'}):
            is_allowed, error_msg = check_trading_permission("place_order")
            assert is_allowed
            assert error_msg == ""

    def test_check_trading_permission_denied(self):
        """Test trading permission when denied."""
        with patch.dict(os.environ, {'SHIOAJI_TRADING_ENABLED': 'false'}):
            is_allowed, error_msg = check_trading_permission("place_order")
            assert not is_allowed
            assert "place_order" in error_msg
            assert "SHIOAJI_TRADING_ENABLED=true" in error_msg

    def test_check_trading_permission_denied_default(self):
        """Test trading permission denied by default."""
        with patch.dict(os.environ, {}, clear=True):
            is_allowed, error_msg = check_trading_permission("cancel_order")
            assert not is_allowed
            assert "cancel_order" in error_msg
            assert "SHIOAJI_TRADING_ENABLED=true" in error_msg