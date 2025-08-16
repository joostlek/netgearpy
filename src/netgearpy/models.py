"""NetgearPy models for device settings."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
from typing import Any

from mashumaro import field_options
from mashumaro.mixins.dict import DataClassDictMixin

from netgearpy.helpers import statistics_to_data, time_to_minutes


class Service(StrEnum):
    """Enum for service types."""

    DEVICE_CONFIG = "DeviceConfig"
    TIME = "Time"
    LAN_CONFIG_SECURITY = "LANConfigSecurity"
    WAN_IP_CONNECTION = "WANIPConnection"
    WAN_ETHERNET_LINK_CONFIG = "WANEthernetLinkConfig"
    PARENTAL_CONTROL = "ParentalControl"
    DEVICE_INFO = "DeviceInfo"
    ADVANCED_QOS = "AdvancedQoS"
    WLAN_CONFIGURATION = "WLANConfiguration"


class DeviceConfigAction(StrEnum):
    """Enum for device config actions."""

    LOGIN = "SOAPLogin"
    LOGOUT = "SOAPLogout"
    REBOOT = "Reboot"
    CHECK_NEW_FIRMWARE = "CheckNewFirmware"
    CHECK_APP_NEW_FIRMWARE = "CheckAppNewFirmware"
    UPDATE_NEW_FIRMWARE = "UpdateNewFirmware"
    CONFIGURATION_STARTED = "ConfigurationStarted"
    CONFIGURATION_FINISHED = "ConfigurationFinished"
    GET_INFO = "GetInfo"
    GET_TIME_ZONE_INFO = "GetTimeZoneInfo"

    GET_DEVICE_LIST_ALL = "GetDeviceListAll"
    GET_BLOCK_DEVICE_ENABLE_STATUS = "GetBlockDeviceEnableStatus"
    SET_BLOCK_DEVICE_ENABLE = "SetBlockDeviceEnable"
    ENABLE_BLOCK_DEVICE_FOR_ALL = "EnableBlockDeviceForAll"
    SET_BLOCK_DEVICE_BY_MAC = "SetBlockDeviceByMAC"

    GET_TRAFFIC_METER_ENABLED = "GetTrafficMeterEnabled"
    GET_TRAFFIC_METER_OPTIONS = "GetTrafficMeterOptions"
    GET_TRAFFIC_METER_STATISTICS = "GetTrafficMeterStatistics"
    ENABLE_TRAFFIC_METER = "EnableTrafficMeter"


class TimeAction(StrEnum):
    """Enum for time actions."""

    GET_INFO = "GetInfo"


class LanConfigSecurityAction(StrEnum):
    """Enum for LAN config security actions."""

    GET_INFO = "GetInfo"


class WanIpConnectionAction(StrEnum):
    """Enum for WAN IP connection actions."""

    GET_INFO = "GetInfo"
    GET_PORT_MAPPING_INFO = "GetPortMappingInfo"
    GET_CONNECTION_TYPE_INFO = "GetConnectionTypeInfo"
    GET_INTERNET_PORT_INFO = "GetInternetPortInfo"


class WanEthernetLinkConfigAction(StrEnum):
    """Enum for WAN Ethernet link config actions."""

    GET_ETHERNET_LINK_STATUS = "GetEthernetLinkStatus"


class ParentalControlAction(StrEnum):
    """Enum for parental control actions."""

    LOGIN = "Authenticate"
    GET_ENABLE_STATUS = "GetEnableStatus"
    ENABLE_PARENTAL_CONTROL = "EnableParentalControl"


class DeviceInfoAction(StrEnum):
    """Enum for device info actions."""

    GET_INFO = "GetInfo"
    GET_SUPPORT_FEATURE_LIST_XML = "GetSupportFeatureListXML"
    GET_ATTACHED_DEVICES = "GetAttachDevice"
    GET_ATTACHED_DEVICES_2 = "GetAttachDevice2"
    SET_NETGEAR_DEVICE_NAME = "SetNetgearDeviceName"
    GET_SYSTEM_LOGS = "GetSystemLogs"
    GET_SYSTEM_INFO = "GetSystemInfo"
    GET_SYSTEM_UPTIME = "GetSysUpTime"


class AdvancedQoSAction(StrEnum):
    """Enum for advanced QoS actions."""

    SET_OOKLA_SPEEDTEST_START = "SetOOKLASpeedTestStart"
    GET_OOKLA_SPEEDTEST_RESULT = "GetOOKLASpeedTestResult"
    GET_QOS_ENABLE_STATUS = "GetQoSEnableStatus"
    SET_QOS_ENABLE_STATUS = "SetQoSEnableStatus"
    GET_BANDWIDTH_CONTROL_OPTIONS = "GetBandwidthControlOptions"
    SET_BANDWIDTH_CONTROL_OPTIONS = "SetBandwidthControlOptions"


class WlanConfigurationAction(StrEnum):
    """Enum for WLAN configuration actions."""

    GET_GUEST_ACCESS_ENABLED = "GetGuestAccessEnabled"  # 2.4G-1 R7800/R8000
    GET_5G_GUEST_ACCESS_ENABLED = "Get5GGuestAccessEnabled"  # 5G-1 R7800
    GET_5G1_GUEST_ACCESS_ENABLED = "Get5G1GuestAccessEnabled"  # 5G-1 R8000
    GET_5G_GUEST_ACCESS_DISABLED_2 = "Get5GGuestAccessEnabled2"  # 5G-2 R8000
    SET_GUEST_ACCESS_ENABLED = "SetGuestAccessEnabled"  # 2.4G-1 R7800
    SET_GUEST_ACCESS_ENABLED_2 = "SetGuestAccessEnabled2"  # 2.4G-1 R8000
    SET_5G_GUEST_ACCESS_ENABLED = "Set5GGuestAccessEnabled"  # 5G-1 R7800
    SET_5G1_GUEST_ACCESS_ENABLED = "Set5G1GuestAccessEnabled"  # 5G-1 R8000
    SET_5G_GUEST_ACCESS_ENABLED_2 = "Set5GGuestAccessEnabled2"  # 5G-2 R8000
    IS_SMART_CONNECT_ENABLED = "IsSmartConnectEnabled"
    SET_SMART_CONNECT_ENABLED = "SetSmartConnectEnable"
    GET_AVAILABLE_CHANNEL = "GetAvailableChannel"
    GET_CHANNEL_INFO = "GetChannelInfo"
    GET_5G_CHANNEL_INFO = "Get5GChannelInfo"
    GET_5G1_CHANNEL_INFO = "Get5G1ChannelInfo"
    SET_CHANNEL = "SetChannel"
    SET_5G_CHANNEL = "Set5GChannel"
    SET_5G1_CHANNEL = "Set5G1Channel"


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


@dataclass
class TrafficMeterStatistics(DataClassDictMixin):
    """Represents the traffic meter statistics."""

    connection_time_today: int = field(
        metadata=field_options(alias="NewTodayConnectionTime")
    )
    upload_today: float = field(metadata=field_options(alias="NewTodayUpload"))
    download_today: float = field(metadata=field_options(alias="NewTodayDownload"))
    connection_time_yesterday: int = field(
        metadata=field_options(alias="NewYesterdayConnectionTime")
    )
    upload_yesterday: float = field(metadata=field_options(alias="NewYesterdayUpload"))
    download_yesterday: float = field(
        metadata=field_options(alias="NewYesterdayDownload")
    )
    connection_time_week: int = field(
        metadata=field_options(alias="NewWeekConnectionTime")
    )
    total_upload_week: float
    average_upload_week: float
    total_download_week: float
    average_download_week: float
    connection_time_month: int = field(
        metadata=field_options(alias="NewMonthConnectionTime")
    )
    total_upload_month: float
    average_upload_month: float
    total_download_month: float
    average_download_month: float
    connection_time_last_month: int = field(
        metadata=field_options(alias="NewLastMonthConnectionTime")
    )
    total_upload_last_month: float
    average_upload_last_month: float
    total_download_last_month: float
    average_download_last_month: float

    @classmethod
    def __pre_deserialize__(cls, d: dict[str, Any]) -> dict[str, Any]:
        """Pre deserialize hook."""
        total_upload_week, average_upload_week = statistics_to_data(d["NewWeekUpload"])
        total_download_week, average_download_week = statistics_to_data(
            d["NewWeekDownload"]
        )
        total_upload_month, average_upload_month = statistics_to_data(
            d["NewMonthUpload"]
        )
        total_download_month, average_download_month = statistics_to_data(
            d["NewMonthDownload"]
        )
        total_upload_last_month, average_upload_last_month = statistics_to_data(
            d["NewLastMonthUpload"]
        )
        total_download_last_month, average_download_last_month = statistics_to_data(
            d["NewLastMonthDownload"]
        )
        return {
            **d,
            "NewTodayConnectionTime": time_to_minutes(d["NewTodayConnectionTime"]),
            "NewYesterdayConnectionTime": time_to_minutes(
                d["NewYesterdayConnectionTime"]
            ),
            "NewWeekConnectionTime": time_to_minutes(d["NewWeekConnectionTime"]),
            "total_upload_week": total_upload_week,
            "average_upload_week": average_upload_week,
            "total_download_week": total_download_week,
            "average_download_week": average_download_week,
            "NewMonthConnectionTime": time_to_minutes(d["NewMonthConnectionTime"]),
            "total_upload_month": total_upload_month,
            "average_upload_month": average_upload_month,
            "total_download_month": total_download_month,
            "average_download_month": average_download_month,
            "NewLastMonthConnectionTime": time_to_minutes(
                d["NewLastMonthConnectionTime"]
            ),
            "total_upload_last_month": total_upload_last_month,
            "average_upload_last_month": average_upload_last_month,
            "total_download_last_month": total_download_last_month,
            "average_download_last_month": average_download_last_month,
        }


@dataclass
class SystemInfo(DataClassDictMixin):
    """Represents the system information."""

    cpu_usage: int = field(metadata=field_options(alias="NewCPUUtilization"))
    memory_usage: int = field(metadata=field_options(alias="NewMemoryUtilization"))
