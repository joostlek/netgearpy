"""Helper functions for NetgearPy."""


def time_to_minutes(source: str) -> int:
    """Convert a time string to minutes."""
    parts = source.split(":")
    if parts[0] == "--" and parts[1] == "--":
        return 0
    hours = int(parts[0])
    minutes = int(parts[1])
    return hours * 60 + minutes


def statistics_to_data(source: str) -> tuple[float, float]:
    """Convert a statistics string to a dictionary."""
    parts = source.split("/")
    return float(parts[0]), float(parts[1])
