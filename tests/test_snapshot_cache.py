from datetime import datetime, timedelta, timezone
from heater_reader.capture import SnapshotCache


def test_snapshot_cache_returns_cached_within_ttl():
    now = datetime(2026, 1, 31, 12, 0, 0, tzinfo=timezone.utc)
    cache = SnapshotCache(ttl_seconds=10)

    cache.set(b"img", width=100, height=50, captured_at=now)

    assert cache.get(now + timedelta(seconds=9)) is not None
    assert cache.get(now + timedelta(seconds=11)) is None
