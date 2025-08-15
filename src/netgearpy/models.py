"""NetgearPy models for device settings."""

from dataclasses import dataclass, field
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
