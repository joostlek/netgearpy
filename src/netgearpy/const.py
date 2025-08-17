"""Constants for NetgearPy."""

from netgearpy.models import Service

ENVELOPE = """<!--?xml version="1.0" encoding= "UTF-8" ?-->
<v:Envelope
xmlns:v="http://schemas.xmlsoap.org/soap/envelope/">
<v:Header>
<SessionID>A7D88AE69687E58D9A00</SessionID>
</v:Header>
<v:Body>
{}
</v:Body>
</v:Envelope>"""

EMPTY_BODY = """<M1:{} xmlns:M1="urn:NETGEAR-ROUTER:service:{}:1" />"""

LOGIN_BODY = """<M1:SOAPLogin xmlns:M1="urn:NETGEAR-ROUTER:service:DeviceConfig:1">
<Username>{}</Username><Password>{}</Password></M1:SOAPLogin>"""


def _get_empty_body(service: Service, object_type: str) -> str:
    """Get an empty body for a SOAP request."""
    return EMPTY_BODY.format(object_type, service)


GET_ATTACHED_DEVICES_BODY = _get_empty_body(Service.DEVICE_INFO, "GetAttachDevice")
GET_ATTACHED_DEVICES_2_BODY = _get_empty_body(Service.DEVICE_INFO, "GetAttachDevice2")

GET_INFO_BODY = _get_empty_body(Service.DEVICE_INFO, "GetInfo")

GET_TRAFFIC_METER_STATISTICS_BODY = _get_empty_body(
    Service.DEVICE_CONFIG, "GetTrafficMeterStatistics"
)

GET_BLOCK_DEVICE_ENABLE_BODY = _get_empty_body(
    Service.DEVICE_CONFIG, "GetBlockDeviceEnableStatus"
)

GET_SYSTEM_INFO_BODY = """<M1:GetSystemInfo xsi:nil="true" />"""

IS_TRAFFIC_METER_ENABLED_BODY = _get_empty_body(
    Service.DEVICE_CONFIG, "GetTrafficMeterEnabled"
)

IS_GUEST_ACCESS_ENABLED_BODY = _get_empty_body(
    Service.WLAN_CONFIGURATION, "GetGuestAccessEnabled"
)

IS_5G_GUEST_ACCESS_ENABLED_BODY = _get_empty_body(
    Service.WLAN_CONFIGURATION, "Get5G1GuestAccessEnabled"
)

IS_QOS_ENABLED_BODY = _get_empty_body(Service.ADVANCED_QOS, "GetQoSEnableStatus")

IS_SMART_CONNECT_ENABLED = _get_empty_body(
    Service.WLAN_CONFIGURATION, "IsSmartConnectEnabled"
)

REBOOT_BODY = _get_empty_body(Service.DEVICE_CONFIG, "Reboot")

IS_PARENTAL_CONTROL_ENABLED_BODY = """<GetEnableStatus></GetEnableStatus>"""

GET_ETHERNET_LINK_STATUS_BODY = """<M1:GetEthernetLinkStatus xsi:nil="true" />"""

START_DEVICE_CONFIGURATION_BODY = """<M1:ConfigurationStarted \
xmlns:M1="urn:NETGEAR-ROUTER:service:DeviceConfig:1">
<NewSessionID>A7D88AE69687E58D9A00</NewSessionID>
</M1:ConfigurationStarted>"""

FINISH_DEVICE_CONFIGURATION_BODY = """<M1:ConfigurationFinished \
xmlns:M1="urn:NETGEAR-ROUTER:service:DeviceConfig:1">
<NewStatus>ChangesApplied</NewStatus>
</M1:ConfigurationFinished>"""
