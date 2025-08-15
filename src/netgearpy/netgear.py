"""Asynchronous Python client for Netgear routers."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self

from aiohttp import ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from netgearpy.models import CurrentSettings

VERSION = metadata.version(__package__)


@dataclass
class NetgearClient:
    """Main class for handling connections with a Netgear router."""

    host: str
    session: ClientSession | None = None
    request_timeout: int = 10
    _close_session: bool = False

    async def _request(
        self,
        url: str,
        *,
        method: str = METH_GET,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Handle a request to a Netgear router."""
        headers = {
            "User-Agent": f"Netgearpy/{VERSION}",
            "Accept": "application/xml",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        async with asyncio.timeout(self.request_timeout):
            response = await self.session.request(
                method,
                url,
                headers=headers,
                json=data,
                params=params,
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
        return CurrentSettings.from_dict(res)

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
