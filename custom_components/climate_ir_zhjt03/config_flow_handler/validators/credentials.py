"""
Credential validators.

Validation functions for user credentials and authentication.

When this file grows, consider splitting into:
- credentials.py: Basic credential validation
- oauth.py: OAuth-specific validation
- api_auth.py: API authentication methods
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_components.climate_ir_zhjt03.api import ClimateZHJT03ApiClient
from homeassistant.helpers.aiohttp_client import async_create_clientsession

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


async def validate_credentials(hass: HomeAssistant, username: str, password: str) -> None:
    """
    Validate user credentials by testing API connection.

    Args:
        hass: Home Assistant instance.
        username: The username to validate.
        password: The password to validate.

    Raises:
        ClimateZHJT03ApiClientAuthenticationError: If credentials are invalid.
        ClimateZHJT03ApiClientCommunicationError: If communication fails.
        ClimateZHJT03ApiClientError: For other API errors.

    """
    client = ClimateZHJT03ApiClient(
        username=username,
        password=password,
        session=async_create_clientsession(hass),
    )
    await client.async_get_data()  # May raise authentication/communication errors


__all__ = [
    "validate_credentials",
]
