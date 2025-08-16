"""Asynchronous Python client for Netgear routers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiohttp.hdrs import METH_POST
from aioresponses import aioresponses
import pytest

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
    ],
    ids=[
        "get_attached_devices",
        "get_device_info",
        "get_traffic_meter_statistics",
        "get_traffic_meter_statistics_2",
        "get_ethernet_link_status",
        "is_block_device_enabled",
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
