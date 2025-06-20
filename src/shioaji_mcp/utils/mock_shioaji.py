"""Mock Shioaji implementation for development and testing."""

import logging

logger = logging.getLogger(__name__)


class MockAccount:
    """Mock account object."""

    def __init__(
        self, account_id: str, broker_id: str = "9A95", account_type: str = "S"
    ):
        self.account_id = account_id
        self.broker_id = broker_id
        self.account_type = account_type
        self.signed = True


class MockContract:
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.symbol = code
        self.currency = "TWD"

class MockSnapshot:
    def __init__(self, code):
        self.close = 100.0 + hash(code) % 50
        self.open = 98.0 + hash(code) % 50
        self.high = 105.0 + hash(code) % 50
        self.low = 95.0 + hash(code) % 50
        self.volume = 1000000 + hash(code) % 500000
        self.bid_price = 99.5 + hash(code) % 50
        self.ask_price = 100.5 + hash(code) % 50
        from datetime import datetime
        self.ts = datetime.now()

class MockContracts:
    def __init__(self):
        self.Stocks = {
            "2330": MockContract("2330", "台積電"),
            "2317": MockContract("2317", "鴻海"),
            "2454": MockContract("2454", "聯發科"),
        }

class MockShioaji:
    """Mock Shioaji API for development."""

    def __init__(self):
        self._logged_in = False
        self._accounts = []
        self.Contracts = MockContracts()

    def login(
        self, api_key: str, secret_key: str, person_id: str, passwd: str
    ) -> list[MockAccount]:
        """Mock login method."""
        logger.info("Mock login called")

        # Simulate login validation
        if not all([api_key, secret_key, person_id, passwd]):
            raise ValueError("Missing credentials")

        # Create mock accounts
        self._accounts = [
            MockAccount("1234567890", "9A95", "S"),
            MockAccount("0987654321", "9A95", "F"),
        ]

        self._logged_in = True
        return self._accounts

    def logout(self):
        """Mock logout method."""
        logger.info("Mock logout called")
        self._logged_in = False
        self._accounts = []

    def list_accounts(self) -> list[MockAccount]:
        """Mock list accounts method."""
        if not self._logged_in:
            raise RuntimeError("Not logged in")
        return self._accounts
    
    def snapshots(self, contracts):
        """Mock snapshots method."""
        return [MockSnapshot(contract.code) for contract in contracts]


# Use mock if real Shioaji fails to import
try:
    import shioaji as sj

    USE_MOCK = False
except ImportError as e:
    logger.warning(f"Failed to import shioaji: {e}. Using mock implementation.")
    sj = type("MockModule", (), {"Shioaji": MockShioaji})()
    USE_MOCK = True
