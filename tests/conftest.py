"""Asynchronous Python client for Netgear routers."""

from collections.abc import AsyncGenerator, Generator
from unittest.mock import patch

import aiohttp
from aioresponses import aioresponses
import pytest

from netgearpy.netgear import NetgearClient
from syrupy import SnapshotAssertion

from .const import IP
from .syrupy import SpotifySnapshotExtension


@pytest.fixture(name="snapshot")
def snapshot_assertion(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the Netgear extension."""
    return snapshot.use_extension(SpotifySnapshotExtension)


@pytest.fixture(name="netgear_client")
async def client() -> AsyncGenerator[NetgearClient, None]:
    """Return a Netgear client."""
    async with (
        aiohttp.ClientSession() as session,
        NetgearClient(IP, session=session) as netgear_client,
    ):
        yield netgear_client


@pytest.fixture(name="responses")
def aioresponses_fixture() -> Generator[aioresponses, None, None]:
    """Return aioresponses fixture."""
    with aioresponses() as mocked_responses:
        yield mocked_responses


@pytest.fixture(autouse=True)
def mock_sleep() -> Generator[None, None, None]:
    """Return aioresponses fixture."""
    with patch("netgearpy.netgear.SLEEP_BETWEEN_CALLS", 0):
        yield
