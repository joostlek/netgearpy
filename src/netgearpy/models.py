"""NetgearPy models for device settings."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
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
    hostname: str | None
    mac_address: str
    connection_type: ConnectionType | None
    link_speed: int | None
    signal_strength: int | None
    blocked: bool | None

    @classmethod
    def from_string(cls, source_string: str) -> AttachedDevice:
        """Pre deserialize hook."""
        parts = source_string.split(";")
        ip_address = parts[1]
        hostname = None
        if parts[2] != "--":
            hostname = parts[2]
        mac_address = parts[3]
        connection_type = None
        link_speed = None
        signal_strength = None
        blocked = None
        if len(parts) >= 7:
            connection_type = ConnectionType(parts[4])
            if parts[5] != "":
                link_speed = int(parts[5])
            signal_strength = int(parts[6])
            if len(parts) >= 8:
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


class DeviceMode(IntEnum):
    """Enum for device modes."""

    ROUTER = 0
    ACCESS_POINT = 1


@dataclass
class DeviceInfo(DataClassDictMixin):
    """Represents the device information."""

    model: str = field(metadata=field_options(alias="ModelName"))
    serial_number: str = field(metadata=field_options(alias="SerialNumber"))
    firmware_version: str = field(metadata=field_options(alias="Firmwareversion"))
    smart_agent_version: str = field(metadata=field_options(alias="SmartAgentversion"))
    firewall_version: str = field(metadata=field_options(alias="FirewallVersion"))
    vpn_version: str | None = field(metadata=field_options(alias="VPNVersion"))
    other_software_version: str = field(
        metadata=field_options(alias="OthersoftwareVersion")
    )
    hardware_version: str = field(metadata=field_options(alias="Hardwareversion"))
    other_hardware_version: str | None = field(
        metadata=field_options(alias="Otherhardwareversion")
    )
    device_name: str = field(metadata=field_options(alias="DeviceName"))
    device_mode: DeviceMode = field(metadata=field_options(alias="DeviceMode"))

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        """Pre deserialize hook."""
        if d["VPNVersion"] == "N/A":
            d["VPNVersion"] = None
        if d["Otherhardwareversion"] == "N/A":
            d["Otherhardwareversion"] = None
        return {**d, "DeviceMode": int(d["DeviceMode"])}
