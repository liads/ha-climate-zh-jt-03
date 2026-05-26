"""Compatibility helpers for infrared-protocols APIs."""

from __future__ import annotations

from importlib import import_module
from typing import Any, cast


def _load_infrared_command() -> type[Any]:
    """Return the infrared-protocols command base class."""
    try:
        module = import_module("infrared_protocols")
        command = vars(module)["Command"]
    except ImportError, KeyError:
        module = import_module("infrared_protocols.commands")
        command = vars(module)["Command"]

    return cast("type[Any]", command)


InfraredCommand = _load_infrared_command()
