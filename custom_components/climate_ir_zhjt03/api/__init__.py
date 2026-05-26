"""
API package for climate_ir_zhjt03.

Architecture:
    Three-layer data flow: Entities → Coordinator → API Client.
    Only the coordinator should call the API client. Entities must never
    import or call the API client directly.

Exception hierarchy:
    ClimateZHJT03ApiClientError (base)
    ├── ClimateZHJT03ApiClientCommunicationError (network/timeout)
    └── ClimateZHJT03ApiClientAuthenticationError (401/403)

Coordinator exception mapping:
    ApiClientAuthenticationError → ConfigEntryAuthFailed (triggers reauth)
    ApiClientCommunicationError → UpdateFailed (auto-retry)
    ApiClientError             → UpdateFailed (auto-retry)
"""

from .client import (
    ClimateZHJT03ApiClient,
    ClimateZHJT03ApiClientAuthenticationError,
    ClimateZHJT03ApiClientCommunicationError,
    ClimateZHJT03ApiClientError,
)

__all__ = [
    "ClimateZHJT03ApiClient",
    "ClimateZHJT03ApiClientAuthenticationError",
    "ClimateZHJT03ApiClientCommunicationError",
    "ClimateZHJT03ApiClientError",
]
