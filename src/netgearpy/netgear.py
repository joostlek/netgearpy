"""Asynchronous Python client for Netgear routers."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self
import xml.etree.ElementTree as ET

from aiohttp import ClientSession
from aiohttp.hdrs import METH_GET, METH_POST
from yarl import URL

from netgearpy.const import (
    ENVELOPE,
    GET_ATTACHED_DEVICES_BODY,
    GET_BLOCK_DEVICE_ENABLE_BODY,
    GET_ETHERNET_LINK_STATUS_BODY,
    GET_INFO_BODY,
    GET_TRAFFIC_METER_STATISTICS_BODY,
    IS_PARENTAL_CONTROL_ENABLED_BODY,
    LOGIN_BODY,
)
from netgearpy.models import (
    AttachedDevice,
    CurrentSettings,
    DeviceConfigAction,
    DeviceInfo,
    DeviceInfoAction,
    ParentalControlAction,
    Service,
    TrafficMeterStatistics,
    WanEthernetLinkConfigAction,
)

VERSION = metadata.version(__package__)


@dataclass
class NetgearClient:
    """Main class for handling connections with a Netgear router."""

    host: str
    session: ClientSession | None = None
    request_timeout: int = 10
    _close_session: bool = False
    _soap_port: int | None = None
    _login_method: int | None = None

    async def _request(
        self,
        url: str,
        *,
        method: str = METH_GET,
        data: str | None = None,
        headers: dict[str, Any] | None = None,
    ) -> str:
        """Handle a request to a Netgear router."""
        base_headers = {
            "User-Agent": f"Netgearpy/{VERSION}",
            "Accept": "application/xml",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        if headers is None:
            headers = {}

        async with asyncio.timeout(self.request_timeout):
            response = await self.session.request(
                method,
                url,
                headers=base_headers | headers,
                data=data,
            )

        return await response.text()

    async def _get(self, uri: str) -> str:
        """Handle a GET request to Netgear."""
        return await self._request(uri, method=METH_GET)

    async def get_current_setting(self) -> CurrentSettings:
        """Get the current settings from the Netgear router."""
        url = URL.build(scheme="http", host=self.host, path="/currentsetting.htm")
        response = await self._get(str(url))
        res: dict[str, Any] = {}
        for entry in response.split("\n"):
            if entry:
                split_entry = entry.split("=")
                res[split_entry[0]] = split_entry[1]
        result = CurrentSettings.from_dict(res)
        self._soap_port = result.https_port
        self._login_method = result.login_method
        return result

    async def _post_xml(
        self, service: str, action: str, body: str
    ) -> dict[str, str | None]:
        """Post XML data to the Netgear router."""
        if self._soap_port is None or self._login_method is None:
            await self.get_current_setting()
        https = self._soap_port in [443, 5555]
        url = URL.build(
            scheme="https" if https else "http",
            host=self.host,
            path="/soap/server_sa/",
            port=self._soap_port,
        )
        headers = {
            "SOAPAction": f"urn:NETGEAR-ROUTER:service:{service}:1#{action}",
        }
        body_str = ENVELOPE.format(body)
        response = await self._request(
            str(url), method=METH_POST, data=body_str, headers=headers
        )
        response_dict = {}
        root = ET.fromstring(response)  # noqa: S314
        for item in root.iter():
            if item.tag != "{http://schemas.xmlsoap.org/soap/envelope/}Body":
                continue
            for child in item:
                for subchild in child:
                    response_dict[subchild.tag] = subchild.text
        return response_dict

    async def login(self, username: str, password: str) -> None:
        """Login to the Netgear router."""
        await self._post_xml(
            Service.DEVICE_CONFIG,
            DeviceConfigAction.LOGIN,
            LOGIN_BODY.format(username, password),
        )

    async def get_attached_devices(self) -> list[AttachedDevice]:
        """Get the attached devices from the Netgear router."""
        response = await self._post_xml(
            Service.DEVICE_INFO,
            DeviceInfoAction.GET_ATTACHED_DEVICES,
            GET_ATTACHED_DEVICES_BODY,
        )
        device_string = response["NewAttachDevice"]
        if not device_string:
            return []
        return [
            AttachedDevice.from_string(entry) for entry in device_string.split("@")[1::]
        ]

    async def is_parental_control_enabled(self) -> bool:
        """Check if parental control is enabled."""
        response = await self._post_xml(
            Service.PARENTAL_CONTROL,
            ParentalControlAction.GET_ENABLE_STATUS,
            IS_PARENTAL_CONTROL_ENABLED_BODY,
        )
        return response.get("ParentalControl") == "1"

    async def is_block_device_enabled(self) -> bool:
        """Check if block device is enabled."""
        response = await self._post_xml(
            Service.DEVICE_CONFIG,
            DeviceConfigAction.GET_BLOCK_DEVICE_ENABLE_STATUS,
            GET_BLOCK_DEVICE_ENABLE_BODY,
        )
        return response.get("ParentalControl") == "1"

    async def get_device_info(self) -> DeviceInfo:
        """Get device information from the Netgear router."""
        response = await self._post_xml(
            Service.DEVICE_INFO, DeviceInfoAction.GET_INFO, GET_INFO_BODY
        )
        return DeviceInfo.from_dict(response)

    async def get_traffic_meter_statistics(self) -> TrafficMeterStatistics:
        """Get traffic meter statistics from the Netgear router."""
        response = await self._post_xml(
            Service.DEVICE_CONFIG,
            DeviceConfigAction.GET_TRAFFIC_METER_STATISTICS,
            GET_TRAFFIC_METER_STATISTICS_BODY,
        )
        return TrafficMeterStatistics.from_dict(response)

    async def get_ethernet_link_status(self) -> str:
        """Get the ethernet link status from the Netgear router."""
        response = await self._post_xml(
            Service.WAN_ETHERNET_LINK_CONFIG,
            WanEthernetLinkConfigAction.GET_ETHERNET_LINK_STATUS,
            GET_ETHERNET_LINK_STATUS_BODY,
        )
        assert response["NewEthernetLinkStatus"] is not None  # noqa: S101
        return response["NewEthernetLinkStatus"]

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The NetgearClient object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
