"""
Entity package for climate_ir_zhjt03.

Architecture:
    All platform entities inherit from (PlatformEntity, ClimateZHJT03Entity).
    MRO order matters — platform-specific class first, then the integration base.
    Entities read data from coordinator.data and NEVER call the API client directly.
    Unique IDs follow the pattern: {entry_id}_{description.key}

See entity/base.py for the ClimateZHJT03Entity base class.
"""

from .base import ClimateZHJT03Entity

__all__ = ["ClimateZHJT03Entity"]
