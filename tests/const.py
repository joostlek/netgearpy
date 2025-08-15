"""Constants for tests."""

from importlib import metadata

IP = "192.168.0.1"
MOCK_URL = f"http://{IP}"

version = metadata.version("netgearpy")

HEADERS = {
    "User-Agent": f"Netgearpy/{version}",
    "Accept": "application/xml",
}
