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

from netgearpy.const import ENVELOPE, GET_ATTACHED_DEVICES_BODY, LOGIN_BODY
from netgearpy.models import AttachedDevice, CurrentSettings

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

    async def _post_xml(self, service: str, action: str, body: str) -> str:
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
        return await self._request(
            str(url), method=METH_POST, data=body_str, headers=headers
        )

    async def login(self, username: str, password: str) -> None:
        """Login to the Netgear router."""
        await self._post_xml(
            "DeviceConfig", "SOAPLogin", LOGIN_BODY.format(username, password)
        )

    async def get_attached_devices(self) -> list[AttachedDevice]:
        """Get the attached devices from the Netgear router."""
        response = await self._post_xml(
            "DeviceInfo",
            "GetAttachedDevices",
            GET_ATTACHED_DEVICES_BODY,
        )
        root = ET.fromstring(response)  # noqa: S314
        for item in root.iter():
            if item.tag != "NewAttachDevice":
                continue
            assert item.text is not None  # noqa: S101
            response = item.text
            break
        devices = []
        first = True
        for entry in response.split("@"):
            if first:
                first = False
                continue
            device = AttachedDevice.from_string(entry)
            devices.append(device)
        return devices

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
