"""Asynchronous Python client for Netgear routers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp.hdrs import METH_POST
from aioresponses import aioresponses
import pytest

from netgearpy.models import (
    AdvancedQoSAction,
    DeviceConfigAction,
    Service,
    WlanConfigurationAction,
)

from . import load_fixture
from .const import HEADERS, MOCK_URL

if TYPE_CHECKING:
    from netgearpy.netgear import NetgearClient
    from syrupy import SnapshotAssertion


def add_soap_response_fixture(
    responses: aioresponses,
    fixture_name: str,
    status: int = 200,
) -> None:
    """Add a SOAP response fixture."""
    responses.post(
        f"{MOCK_URL}/soap/server_sa/",
        status=status,
        body=load_fixture(fixture_name),
    )


def check_soap_called(
    responses: aioresponses,
    soap_action: str,
    body: str,
) -> None:
    """Check if the SOAP request was called with the expected parameters."""
    responses.assert_called_with(
        f"{MOCK_URL}/soap/server_sa/",
        METH_POST,
        headers=HEADERS | {"SOAPAction": soap_action},
        data=f"""<!--?xml version="1.0" encoding= "UTF-8" ?-->\n<v:Envelope\nxmlns:v="http://schemas.xmlsoap.org/soap/envelope/">\n<v:Header>\n<SessionID>A7D88AE69687E58D9A00</SessionID>\n</v:Header>\n<v:Body>\n{body}\n</v:Body>\n</v:Envelope>""",
    )


async def test_get_current_setting(
    responses: aioresponses, snapshot: SnapshotAssertion, netgear_client: NetgearClient
) -> None:
    """Test get current router setting."""
    responses.get(
        "http://192.168.0.1/currentsetting.htm",
        status=200,
        body=load_fixture("current_setting.txt"),
    )
    assert await netgear_client.get_current_setting() == snapshot


async def test_login(responses: aioresponses, netgear_client: NetgearClient) -> None:
    """Test login to the Netgear router."""
    responses.get(
        "http://192.168.0.1/currentsetting.htm",
        status=200,
        body=load_fixture("current_setting.txt"),
    )
    add_soap_response_fixture(responses, "login_response.xml")
    await netgear_client.login("username", "password")
    check_soap_called(
        responses,
        "urn:NETGEAR-ROUTER:service:DeviceConfig:1#SOAPLogin",
        """<M1:SOAPLogin xmlns:M1="urn:NETGEAR-ROUTER:service:DeviceConfig:1">
<Username>username</Username><Password>password</Password></M1:SOAPLogin>""",
    )


@pytest.mark.parametrize(
    ("fixture_name", "method", "soap_service", "soap_action", "expected_body"),
    [
        (
            "GetAttachDevice.xml",
            "get_attached_devices",
            "DeviceInfo",
            "GetAttachDevice",
            """<M1:GetAttachDevice xmlns:M1="urn:NETGEAR-ROUTER:service:DeviceInfo:1" />""",
        ),
        (
            "GetAttachDevice2.xml",
            "get_attached_devices_2",
            "DeviceInfo",
            "GetAttachDevice2",
            """<M1:GetAttachDevice2 xmlns:M1="urn:NETGEAR-ROUTER:service:DeviceInfo:1" />""",
        ),
        (
            "DeviceInfo.xml",
            "get_device_info",
            "DeviceInfo",
            "GetInfo",
            """<M1:GetInfo xmlns:M1="urn:NETGEAR-ROUTER:service:DeviceInfo:1" />""",
        ),
        (
            "GetTrafficMeterStatistics.xml",
            "get_traffic_meter_statistics",
            "DeviceConfig",
            "GetTrafficMeterStatistics",
            """<M1:GetTrafficMeterStatistics xmlns:M1="urn:NETGEAR-ROUTER:service:DeviceConfig:1" />""",
        ),
        (
            "GetTrafficMeterStatistics2.xml",
            "get_traffic_meter_statistics",
            "DeviceConfig",
            "GetTrafficMeterStatistics",
            """<M1:GetTrafficMeterStatistics xmlns:M1="urn:NETGEAR-ROUTER:service:DeviceConfig:1" />""",
        ),
        (
            "GetSystemInfo.xml",
            "get_system_info",
            "DeviceInfo",
            "GetSystemInfo",
            """<M1:GetSystemInfo xsi:nil="true" />""",
        ),
        (
            "GetEthernetLinkStatus.xml",
            "get_ethernet_link_status",
            "WANEthernetLinkConfig",
            "GetEthernetLinkStatus",
            """<M1:GetEthernetLinkStatus xsi:nil="true" />""",
        ),
        (
            "GetBlockDeviceEnableStatus.xml",
            "is_block_device_enabled",
            "DeviceConfig",
            "GetBlockDeviceEnableStatus",
            """<M1:GetBlockDeviceEnableStatus xmlns:M1="urn:NETGEAR-ROUTER:service:DeviceConfig:1" />""",
        ),
        (
            "GetTrafficMeterEnabled.xml",
            "is_traffic_meter_enabled",
            "DeviceConfig",
            "GetTrafficMeterEnabled",
            """<M1:GetTrafficMeterEnabled xmlns:M1="urn:NETGEAR-ROUTER:service:DeviceConfig:1" />""",
        ),
        (
            "GetGuestAccessEnabled.xml",
            "is_guest_access_enabled",
            Service.WLAN_CONFIGURATION,
            WlanConfigurationAction.GET_GUEST_ACCESS_ENABLED,
            """<M1:GetGuestAccessEnabled xmlns:M1="urn:NETGEAR-ROUTER:service:WLANConfiguration:1" />""",
        ),
        (
            "Get5GGuestAccessEnabled.xml",
            "is_5g_guest_access_enabled",
            Service.WLAN_CONFIGURATION,
            WlanConfigurationAction.GET_5G1_GUEST_ACCESS_ENABLED_2,
            """<M1:Get5G1GuestAccessEnabled xmlns:M1="urn:NETGEAR-ROUTER:service:WLANConfiguration:1" />""",
        ),
        (
            "GetQoSEnableStatus.xml",
            "is_qos_enabled",
            Service.ADVANCED_QOS,
            AdvancedQoSAction.GET_QOS_ENABLE_STATUS,
            """<M1:GetQoSEnableStatus xmlns:M1="urn:NETGEAR-ROUTER:service:AdvancedQoS:1" />""",
        ),
        (
            "GetSmartConnectEnabled.xml",
            "is_smart_connect_enabled",
            Service.WLAN_CONFIGURATION,
            WlanConfigurationAction.IS_SMART_CONNECT_ENABLED,
            """<M1:IsSmartConnectEnabled xmlns:M1="urn:NETGEAR-ROUTER:service:WLANConfiguration:1" />""",
        ),
    ],
    ids=[
        "get_attached_devices",
        "get_attached_devices_2",
        "get_device_info",
        "get_traffic_meter_statistics",
        "get_traffic_meter_statistics_2",
        "get_system_info",
        "get_ethernet_link_status",
        "is_block_device_enabled",
        "is_traffic_meter_enabled",
        "is_guest_access_enabled",
        "is_5g_guest_access_enabled",
        "is_qos_enabled",
        "is_smart_connect_enabled",
    ],
)
async def test_get_data(  # pylint: disable=too-many-positional-arguments
    responses: aioresponses,
    snapshot: SnapshotAssertion,
    netgear_client: NetgearClient,
    fixture_name: str,
    method: str,
    soap_service: str,
    soap_action: str,
    expected_body: str,
) -> None:
    """Test get attached devices."""
    responses.get(
        "http://192.168.0.1/currentsetting.htm",
        status=200,
        body=load_fixture("current_setting.txt"),
    )
    add_soap_response_fixture(responses, fixture_name)
    assert await getattr(netgear_client, method)() == snapshot
    check_soap_called(
        responses,
        f"urn:NETGEAR-ROUTER:service:{soap_service}:1#{soap_action}",
        expected_body,
    )


@pytest.mark.parametrize(
    ("fixture_name", "method"),
    [
        (
            "Reboot.xml",
            "reboot",
        ),
    ],
    ids=[
        "reboot",
    ],
)
async def test_device_configuration_mode_calls(  # pylint: disable=too-many-positional-arguments
    responses: aioresponses,
    snapshot: SnapshotAssertion,
    netgear_client: NetgearClient,
    fixture_name: str,
    method: str,
) -> None:
    """Test device configuration mode calls."""
    responses.get(
        "http://192.168.0.1/currentsetting.htm",
        status=200,
        body=load_fixture("current_setting.txt"),
    )
    add_soap_response_fixture(responses, "ConfigurationStart.xml")
    add_soap_response_fixture(responses, fixture_name)
    add_soap_response_fixture(responses, "ConfigurationFinished.xml")
    assert await getattr(netgear_client, method)() == snapshot
    check_soap_called(
        responses,
        f"urn:NETGEAR-ROUTER:service:{Service.DEVICE_CONFIG}:1#{DeviceConfigAction.CONFIGURATION_FINISHED}",
        """<M1:ConfigurationFinished xmlns:M1="urn:NETGEAR-ROUTER:service:DeviceConfig:1">
<NewStatus>ChangesApplied</NewStatus>
</M1:ConfigurationFinished>""",
    )


async def test_is_parental_control_enabled(
    responses: aioresponses, netgear_client: NetgearClient
) -> None:
    """Test get attached devices."""
    responses.get(
        "http://192.168.0.1/currentsetting.htm",
        status=200,
        body=load_fixture("current_setting.txt"),
    )
    add_soap_response_fixture(responses, "ParentalControlGetEnableStatus.xml")
    assert not await netgear_client.is_parental_control_enabled()
    check_soap_called(
        responses,
        "urn:NETGEAR-ROUTER:service:ParentalControl:1#GetEnableStatus",
        """<GetEnableStatus></GetEnableStatus>""",
    )
