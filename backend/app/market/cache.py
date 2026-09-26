"""Thread-safe in-memory price cache."""

from __future__ import annotations

import time
from collections import deque
from threading import Lock

from .models import PriceUpdate


class PriceCache:
    """Thread-safe in-memory cache of the latest price for each ticker.

    Also keeps the last `history_size` updates per ticker, so charts can be
    populated on page load.

    Writers: SimulatorDataSource or MassiveDataSource (one at a time).
    Readers: SSE streaming endpoint, price history endpoint, portfolio valuation,
    trade execution.
    """

    def __init__(self, history_size: int = 300) -> None:
        self._prices: dict[str, PriceUpdate] = {}
        self._history: dict[str, deque[PriceUpdate]] = {}
        self._history_size = history_size
        self._lock = Lock()
        self._version: int = 0  # Monotonically increasing; bumped on every update

    def update(self, ticker: str, price: float, timestamp: float | None = None) -> PriceUpdate:
        """Record a new price for a ticker. Returns the created PriceUpdate.

        Automatically computes direction and change from the previous price.
        If this is the first update for the ticker, previous_price == price (direction='flat').
        """
        with self._lock:
            ts = timestamp or time.time()
            prev = self._prices.get(ticker)
            previous_price = prev.price if prev else price

            update = PriceUpdate(
                ticker=ticker,
                price=round(price, 2),
                previous_price=round(previous_price, 2),
                timestamp=ts,
            )
            self._prices[ticker] = update
            self._history.setdefault(ticker, deque(maxlen=self._history_size)).append(update)
            self._version += 1
            return update

    def get(self, ticker: str) -> PriceUpdate | None:
        """Get the latest price for a single ticker, or None if unknown."""
        with self._lock:
            return self._prices.get(ticker)

    def get_all(self) -> dict[str, PriceUpdate]:
        """Snapshot of all current prices. Returns a shallow copy."""
        with self._lock:
            return dict(self._prices)

    def get_history(self, ticker: str) -> list[PriceUpdate]:
        """Recent updates for a ticker, oldest first. Empty if unknown."""
        with self._lock:
            return list(self._history.get(ticker, ()))

    def get_price(self, ticker: str) -> float | None:
        """Convenience: get just the price float, or None."""
        update = self.get(ticker)
        return update.price if update else None

    def remove(self, ticker: str) -> None:
        """Remove a ticker and its history (e.g., when no longer tracked)."""
        with self._lock:
            self._prices.pop(ticker, None)
            self._history.pop(ticker, None)

    @property
    def version(self) -> int:
        """Current version counter. Useful for SSE change detection."""
        return self._version

    def __len__(self) -> int:
        with self._lock:
            return len(self._prices)

    def __contains__(self, ticker: str) -> bool:
        with self._lock:
            return ticker in self._prices
