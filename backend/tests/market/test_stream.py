"""Tests for the SSE event generator."""

import json

from app.market.cache import PriceCache
from app.market.stream import _generate_events


class FakeRequest:
    """Stands in for a Starlette Request that disconnects after `checks` polls."""

    client = None

    def __init__(self, checks: int) -> None:
        self._remaining = checks

    async def is_disconnected(self) -> bool:
        self._remaining -= 1
        return self._remaining < 0


async def collect(cache: PriceCache, checks: int, keepalive: float = 10.0) -> list[str]:
    """Run the generator for `checks` loop iterations and return every chunk."""
    events = _generate_events(cache, FakeRequest(checks), interval=0.0, keepalive=keepalive)
    return [chunk async for chunk in events]


class TestGenerateEvents:
    """Unit tests for _generate_events."""

    async def test_starts_with_retry_directive(self):
        chunks = await collect(PriceCache(), checks=0)
        assert chunks == ["retry: 1000\n\n"]

    async def test_sends_all_tickers_keyed_by_ticker(self):
        cache = PriceCache()
        cache.update("AAPL", 190.0)
        cache.update("GOOGL", 175.0)
        chunks = await collect(cache, checks=1)
        assert chunks[1].startswith("data: ")
        payload = json.loads(chunks[1].removeprefix("data: "))
        assert set(payload) == {"AAPL", "GOOGL"}
        assert payload["AAPL"]["price"] == 190.0

    async def test_no_repeat_event_when_unchanged(self):
        cache = PriceCache()
        cache.update("AAPL", 190.0)
        chunks = await collect(cache, checks=3)
        assert sum(c.startswith("data: ") for c in chunks) == 1

    async def test_keepalive_when_idle(self):
        chunks = await collect(PriceCache(), checks=2, keepalive=0.0)
        assert ": keepalive\n\n" in chunks

    async def test_no_keepalive_while_prices_flow(self):
        cache = PriceCache()
        cache.update("AAPL", 190.0)
        chunks = await collect(cache, checks=1, keepalive=10.0)
        assert ": keepalive\n\n" not in chunks
