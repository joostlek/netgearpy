"""NetgearPy models for device settings."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from mashumaro import field_options
from mashumaro.mixins.dict import DataClassDictMixin


@dataclass
class CurrentSettings(DataClassDictMixin):
    """Represents the current setting of a device."""

    firmware_version: str = field(metadata=field_options(alias="Firmware"))
    model: str = field(metadata=field_options(alias="Model"))
    login_method: int = field(metadata=field_options(alias="LoginMethod"))
    https_port: int = field(metadata=field_options(alias="SOAP_HTTPs_Port"))

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        """Pre deserialize hook."""
        return {
            **d,
            "LoginMethod": int(float(d["LoginMethod"])),
        }


class ConnectionType(StrEnum):
    """Enum for connection types."""

    WIRED = "wired"
    WIRELESS = "wireless"


@dataclass(kw_only=True)
class AttachedDevice:
    """Represents an attached device."""

    ip_address: str
    hostname: str | None = None
    mac_address: str
    connection_type: ConnectionType
    link_speed: int | None = None
    signal_strength: int
    blocked: bool

    @classmethod
    def from_string(cls, source_string: str) -> AttachedDevice:
        """Pre deserialize hook."""
        parts = source_string.split(";")
        ip_address = parts[1]
        hostname = None
        if parts[2] != "--":
            hostname = parts[2]
        mac_address = parts[3]
        connection_type = ConnectionType(parts[4])
        link_speed = None
        if parts[5] != "":
            link_speed = int(parts[5])
        signal_strength = int(parts[6])
        blocked = parts[7] != "Allow"
        return AttachedDevice(
            ip_address=ip_address,
            hostname=hostname,
            mac_address=mac_address,
            connection_type=connection_type,
            link_speed=link_speed,
            signal_strength=signal_strength,
            blocked=blocked,
        )
