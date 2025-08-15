"""Asynchronous Python client for Netgear routers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aioresponses import aioresponses

from . import load_fixture

if TYPE_CHECKING:
    from netgearpy.netgear import NetgearClient
    from syrupy import SnapshotAssertion


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
