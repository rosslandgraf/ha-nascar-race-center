"""Shared fixtures for offline Home Assistant integration tests."""

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Load the integration from this checkout through Home Assistant's loader."""
