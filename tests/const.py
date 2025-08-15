"""Constants for tests."""

from importlib import metadata

IP = "192.168.0.1"
MOCK_URL = f"https://{IP}:5555"

version = metadata.version("netgearpy")

HEADERS = {
    "User-Agent": f"Netgearpy/{version}",
    "Accept": "application/xml",
}
